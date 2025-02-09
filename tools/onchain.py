import requests
from config import settings
from pool import pool
import time
import json
from phi.agent import Agent
from phi.tools import Toolkit
from phi.utils.log import logger
from app.utils.requests import retry_request


class OnchainTool(Toolkit):
    base_url = settings.SERVICE_ONCHAIN_BASE_URL

    def __init__(self):
        super().__init__(name="onchain_tools")
        self.register(self.check_balance)
        self.register(self.check_balance_all_tokens)
        self.register(self.swap_token)
        self.register(self.limit_order)
        self.register(self.cancel_all_orders)

    def check_balance_all_tokens(self, agent: Agent) -> str:
        """
        Use this tool to check the balance of a user in all tokens.
        Returns:
            str: Balance of the user in all tokens.
        """
        user_id = agent.context.get("user_id", None)
        if user_id is None:
            return "User does not exist"
        with pool.connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM wallets WHERE user_id = %s", (user_id,))
            wallets = cursor.fetchone()
            if wallets is None:
                return "User does not have a wallet"
            # private_key = wallets[4]
            public_key: str = wallets[3]

            def get_balances(address: str) -> dict:
                res = requests.get(
                    f"{self.base_url}/allTokens",
                    params={"address": address},
                )
                res.raise_for_status()
                return res.json()

            return retry_request(get_balances, retries=3, delay=5)(public_key)

    def check_balance(self, agent: Agent, token_address: str) -> str:
        """
        Use this tool to check the balance of a user in a token.
        Args:
            token_address (str): Mint address of the token. Default is SUI. with address "0x2::sui::SUI"
        Returns:
            str: Balance of the user in the token.
        """
        user_id = agent.context["user_id"]
        with pool.connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM wallets WHERE user_id = %s", (user_id,))
            wallet = cursor.fetchone()  # tuple
            if wallet is None:
                logger.error(f"[TOOLS] User {user_id} does not have a wallet")
                return "User does not have a wallet"
            public_key = wallet[3]

            def get_balance(public_key: str, token_address: str) -> str:
                res = requests.post(
                    f"{settings.SERVICE_JUPITER_BASE_URL}/balance",
                    json={"address": public_key, "tokenAddress": token_address},
                )
                res.raise_for_status()
                return str(res.json().get("balance", None))  # Return balance as string

            balance = retry_request(get_balance, retries=3, delay=5)(
                public_key, token_address
            )
            return balance

    def swap_token(
        self,
        agent: Agent,
        input_amount: float,
        input_mint_address: str,
        output_mint_address: str,
    ) -> str:
        """
        Use this tool to swap tokens. Always notify the user about the addresses of tokens.
        Args:
            input_amount (float): Amount of input token to swap. > 0
            input_mint_address (str): Mint address of input token. It must be a valid mint address. Example: "0xdba34672e30cb065b1f93e3ab55318768fd6fef66c15942c9f7cb846e2f900e7::usdc::USDC"
            output_mint_address (str): Mint address of output token. It must be a valid mint address. Example: "0x2::sui::SUI"
        Returns:
            str: Transaction hash or error message.
        """
        user_id = agent.context["user_id"]

        logger.info(
            f"[TOOLS] Swapping {input_amount} {input_mint_address} to {output_mint_address} for user: {agent.context['user_id']}"
        )
        ## CALL JUPITER API
        with pool.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM wallets WHERE user_id = %s",
                (user_id,),
            )
            wallet = cursor.fetchone()  # tuple
            if wallet is None:
                logger.error(f"[TOOLS] User {user_id} does not have a wallet")
                return "User does not have a wallet"
            private_key = wallet[4]

            balance = float(self.check_balance(agent, input_mint_address))
            if balance < input_amount:
                logger.error(f"[TOOLS] Insufficient balance for user: {user_id}")
                return "Insufficient balance"

            def _swap(
                private_key: str,
                input_amount: float,
                input_mint_address: str,
                output_mint_address: str,
            ) -> str:
                body = {
                    "inputAmount": input_amount,
                    "inputMint": input_mint_address,
                    "outputMint": output_mint_address,
                    "privateKey": private_key,
                }
                response = requests.post(
                    f"{settings.SERVICE_JUPITER_BASE_URL}/swap",
                    json=body,
                )
                logger.info(f"Response: {response}")
                try:
                    res = response.json()
                except requests.exceptions.JSONDecodeError:
                    # Handle empty or invalid JSON response
                    logger.error(
                        f"Error: Invalid response received. Status code: {response.status_code}"
                    )
                    logger.error(f"Response text: {response.text}")
                    return response.text
                if res["status"] is True:
                    logger.info(
                        f"[TOOLS] Swapped {input_amount} {input_mint_address} to {output_mint_address} for user: {user_id}"
                    )
                    return res["data"]
                else:
                    raise Exception(
                        f"[TOOLS] Failed to swap {input_amount} {input_mint_address} to {output_mint_address} for user: {user_id}"
                    )

            return retry_request(_swap, retries=3, delay=5)(
                private_key, input_amount, input_mint_address, output_mint_address
            )

    def limit_order(
        self,
        agent: Agent,
        maker_amount: float,
        taker_amount: float,
        maker_mint: str,
        taker_mint: str,
    ) -> str:
        """
        Use this tool to create a limit order. Always notify the user about the addresses of tokens.
        Args:
            maker_amount (float): Amount of maker token to swap. > 0
            taker_amount (float): Amount of taker token to swap. > 0
            maker_mint (str): Mint address of maker token. It must be a valid mint address. Example: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            taker_mint (str): Mint address of taker token. It must be a valid mint address. Example: "So11111111111111111111111111111111111111112"
        Returns:
            str: Transaction hash or error message.
        """
        # if maker_amount < 5:
        #     return "Maker amount must be greater than 5"
        user_id = agent.context["user_id"]
        logger.info(f"[TOOLS] Creating limit order for user: {user_id}")
        with pool.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM wallets WHERE user_id = %s",
                (user_id,),
            )
            wallet = cursor.fetchone()  # tuple
            private_key = wallet[4]
            balance = float(self.check_balance(agent, maker_mint))
            if balance < maker_amount:
                logger.error(f"[TOOLS] Insufficient balance for user: {user_id}")
                return "Insufficient balance"

            def _limit_order(
                private_key: str,
                maker_amount: float,
                taker_amount: float,
                maker_mint: str,
                taker_mint: str,
            ) -> str:
                body = {
                    "makingAmount": maker_amount,
                    "takingAmount": taker_amount,
                    "inputMint": maker_mint,
                    "outputMint": taker_mint,
                    "privateKey": private_key,
                }
                response = requests.post(
                    f"{settings.SERVICE_JUPITER_BASE_URL}/limitOrder",
                    json=body,
                )
                logger.info(f"Response: {response}")
                try:
                    res = response.json()
                except requests.exceptions.JSONDecodeError:
                    # Handle empty or invalid JSON response
                    logger.error(
                        f"Error: Invalid response received. Status code: {response.status_code}"
                    )
                    logger.error(f"Response text: {response.text}")
                    return response.text
                if res["status"] is True:
                    logger.info(f"[TOOLS] Created limit order for user: {user_id}")
                    return res["data"]
                else:
                    raise Exception(
                        f"[TOOLS] Failed to create limit order for user: {user_id}"
                    )

            return retry_request(_limit_order, retries=3, delay=5)(
                private_key,
                maker_amount,
                taker_amount,
                maker_mint,
                taker_mint,
            )

    def cancel_all_orders(self, agent: Agent) -> str:
        """
        Use this tool to cancel all orders for a user.
        Args:

        Returns:
            str: status of the request
        """
        user_id = agent.context["user_id"]
        logger.info(f"[TOOLS] Cancelling all orders for user: {user_id}")
        with pool.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM wallets WHERE user_id = %s",
                (user_id,),
            )
            wallet = cursor.fetchone()  # tuple
            private_key = wallet[4]

            def _cancel_all_orders(private_key: str) -> str:
                response = requests.post(
                    f"{settings.SERVICE_JUPITER_BASE_URL}/cancelOrders",
                    json={
                        "privateKey": private_key,
                    },
                )
                logger.info(f"Response: {response}")
                try:
                    res = response.json()
                except requests.exceptions.JSONDecodeError:
                    # Handle empty or invalid JSON response
                    logger.error(
                        f"Error: Invalid response received. Status code: {response.status_code}"
                    )
                    logger.error(f"Response text: {response.text}")
                    return response.text
                if res["status"] is True:
                    logger.info(f"[TOOLS] Cancelled all orders for user: {user_id}")
                    return res["data"]
                else:
                    raise Exception(
                        f"[TOOLS] Failed to cancel all orders for user: {user_id}"
                    )

            return retry_request(_cancel_all_orders, retries=3, delay=5)(private_key)
