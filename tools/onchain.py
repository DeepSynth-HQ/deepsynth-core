import requests
from config import settings
from pool import pool
import time
import json
from phi.agent import Agent
from phi.tools import Toolkit
from phi.utils.log import logger
from app.utils.requests import retry_request
from log import logger


class OnchainTool(Toolkit):
    base_url = settings.SERVICE_ONCHAIN_BASE_URL

    def __init__(self):
        super().__init__(name="onchain_tools")
        self.register(self.check_balance)
        self.register(self.check_balance_all_tokens)
        self.register(self.get_pool_info_by_symbols)
        self.register(self.get_pool_info_by_id_to_swap)
        self.register(self.get_token_address_by_symbol)
        self.register(self.swap_token)

    def _extract_wallet(self, user_id: str) -> dict | None:
        with pool.connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM wallets WHERE user_id = %s", (user_id,))
            wallet = cursor.fetchone()
            if wallet is None:
                return None
            data = {
                "private_key": wallet[4],
                "public_key": wallet[3],
            }
            return data

    def check_balance_all_tokens(self, agent: Agent) -> str:
        """
        Use this tool to check the balance of a user in all tokens.
        Returns:
            str: Balance of the user in all tokens.
        """
        user_id = agent.context.get("user_id", None)
        logger.debug(f"[TOOLS] Checking balance of all tokens for user: {user_id}")
        if user_id is None:
            return "User does not exist"
        wallet = self._extract_wallet(user_id)
        if wallet is None:
            return "User does not have a wallet"
        public_key: str = wallet["public_key"]
        logger.debug(f"[TOOLS] Public key: {public_key}")

        def get_balances(address: str) -> dict:
            res = requests.get(
                f"{self.base_url}/allTokens",
                params={"address": address},
            )
            logger.debug(f"[TOOLS] Response: {res}")
            res.raise_for_status()
            return res.text

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
        wallet = self._extract_wallet(user_id)
        if wallet is None:
            logger.error(f"[TOOLS] User {user_id} does not have a wallet")
            return "User does not have a wallet"
        public_key = wallet["public_key"]

        def get_balance(public_key: str, token_address: str) -> str:
            res = requests.get(
                f"{self.base_url}/balance",
                params={"address": public_key, "coinType": token_address},
            )
            res.raise_for_status()
            return str(res.json().get("data", None))  # Return balance as string

        return retry_request(get_balance, retries=3, delay=5)(public_key, token_address)

    def get_pool_info_by_symbols(self, coinA: str, coinB: str) -> str:
        """
        Use this tool to get the pool info of a token.
        Args:
            coinA (str): Symbol of the first token.
            coinB (str): Symbol of the second token.
        Returns:
            str: Pool info of the token.
        """

        def _fetch_pool_info(coinA: str, coinB: str) -> str:
            res = requests.get(
                f"{self.base_url}/getPool",
                params={"coinA": coinA, "coinB": coinB},
            )
            res.raise_for_status()
            return res.text

        return retry_request(_fetch_pool_info, retries=3, delay=5)(coinA, coinB)

    def get_pool_info_by_id_to_swap(self, pool_id: str) -> str:
        """
        Use this tool to get the pool info of a token.
        Args:
            pool_id (str): ID of the pool.
        Returns:
            str: Pool info of the token.
        """

        def _fetch_pool_info(pool_id: str) -> str:
            res = requests.get(
                f"{self.base_url}/poolInfo",
                params={"poolId": pool_id},
            )
            res.raise_for_status()
            return res.text

        return retry_request(_fetch_pool_info, retries=3, delay=5)(pool_id)

    def get_token_address_by_symbol(self, symbol: str) -> str:
        """
        Use this tool to get the token info of a symbol.
        Args:
            symbol (str): Symbol of the token.
        Returns:
            str: Token info of the symbol. Includes mint address
        """

        def _fetch_token_info(symbol: str) -> str:
            res = requests.get(
                f"{self.base_url}/tokensByName",
                params={"name": symbol},
            )
            res.raise_for_status()
            return res.text

        return retry_request(_fetch_token_info, retries=3, delay=5)(symbol)

    def swap_token(
        self,
        agent: Agent,
        pool_id: str,
        input_amount: float,
        a_to_b: bool,
    ) -> str:
        """
        Use this tool to swap tokens. Always notify the user about the addresses of tokens. a_to_b is True if swap from A to B, False if swap from B to A. If swap from A to B it means sell A to B,
        Args:
            pool_id (str): ID of the pool. This can be obtained from get_pool_info_by_symbols
            input_amount (float): Amount of input token to swap. > 0
            a_to_b (bool): True swap from A to B, False swap from B to A. Check the pool info to see which is which.
        Returns:
            str: Transaction hash or error message.
        """
        user_id = agent.context["user_id"]
        logger.debug(f"[TOOLS] Swapping token for user: {user_id}")
        wallet = self._extract_wallet(user_id)
        if wallet is None:
            logger.error(f"[TOOLS] User {user_id} does not have a wallet")
            return "User does not have a wallet"
        private_key = wallet["private_key"]
        public_key = wallet["public_key"]
        logger.debug(f"[TOOLS] Private key: {private_key}")
        logger.debug(f"[TOOLS] Public key: {public_key}")

        def _swap_token(
            private_key: str,
            pool_id: str,
            input_amount: float,
            a_to_b: bool,
        ) -> str:
            body = {
                "poolId": pool_id,
                "inputAmount": input_amount,
                "aToB": a_to_b,
                "privateKey": private_key,
            }
            response = requests.post(
                f"{self.base_url}/swap",
                json=body,
            )
            logger.info(f"Response: {response}")
            try:
                res = response.json()
            except requests.exceptions.JSONDecodeError:
                logger.error(
                    f"Error: Invalid response received. Status code: {response.status_code}"
                )
                logger.error(f"Response text: {response.text}")
                return response.text
            if res["status"] is True:
                logger.info(f"[TOOLS] Swapped token for user: {user_id}")
                return res["data"]
            else:
                raise Exception(
                    f"[TOOLS] Failed to swap token for user: {user_id}, error: {res}"
                )

        return retry_request(_swap_token, retries=3, delay=5)(
            private_key,
            pool_id,
            input_amount,
            a_to_b,
        )
