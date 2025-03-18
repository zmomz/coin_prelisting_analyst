import httpx
from app.core.config import settings


async def get_coingeko_ids():
    """Fetch CoinGecko coin IDs and symbols."""
    url = f"{settings.COINGECKO_API_URL}/coins/list"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            data = response.json()
            data.export("data.json")
            return {"success": True}
        else:
            print(f"❌ Failed to fetch CoinGecko coin IDs: {response.text}")
            return {}

data = {
  "id": "solana",
  "symbol": "sol",
  "name": "Solana",
  "description": {
    "en": "Solana is a highly functional open source project that banks on blockchain technology’s permissionless nature to provide decentralized finance (DeFi) solutions. It is a layer 1 network that offers fast speeds and affordable costs. While the idea and initial work on the project began in 2017, Solana was officially launched in March 2020 by the Solana Foundation with headquarters in Geneva, Switzerland."
  },
  "links": {
    "homepage": [
      "https://solana.com/"
    ],
    "blockchain_site": [
      "https://solscan.io/",
      "https://platform.arkhamintelligence.com/explorer/token/solana",
      "https://xray.helius.xyz/",
      "https://solana.fm/",
      "https://solanabeach.io/",
      "https://www.oklink.com/sol",
      "https://explorer.solana.com/"
    ],
    "twitter_screen_name": "solana",
    "telegram_channel_identifier": "solana",
    "subreddit_url": "https://www.reddit.com/r/solana",
    "repos_url": {
      "github": [
        "https://github.com/solana-labs/solana"
      ]
    }
  },
  "image": {
    "thumb": "https://coin-images.coingecko.com/coins/images/4128/thumb/solana.png?1718769756",
    "small": "https://coin-images.coingecko.com/coins/images/4128/small/solana.png?1718769756",
    "large": "https://coin-images.coingecko.com/coins/images/4128/large/solana.png?1718769756"
  },
  "market_cap_rank": 6,
  "market_data": {
    "ath": {
      "usd": 293.31
    },
    "ath_change_percentage": {
      "usd": -55.91517
    },
    "atl": {
      "usd": 0.500801
    },
    "atl_change_percentage": {
      "usd": 25719.84081
    },
    "atl_date": {
      "usd": "2020-05-11T19:35:23.449Z"
    },
    "market_cap": {
      "usd": 65887816838
    },
    "market_cap_rank": 6,
    "fully_diluted_valuation": {
      "usd": 77053357976
    },
    "total_volume": {
      "usd": 2769737550
    },
    "high_24h": {
      "usd": 130.78
    },
    "low_24h": {
      "usd": 125.59
    },
    "circulating_supply": 509925207.573872,
    "last_updated": "2025-03-17T12:00:33.504Z"
  },
  "community_data": {
    "twitter_followers": 3325637,
    "telegram_channel_user_count": 72250
  },
  "developer_data": {
    "forks": 3516,
    "stars": 11071,
    "subscribers": 276,
    "total_issues": 5177,
    "closed_issues": 4611,
    "pull_requests_merged": 23614,
    "pull_request_contributors": 411,
    "code_additions_deletions_4_weeks": {
      "additions": 10193,
      "deletions": -5277
    },
    "commit_count_4_weeks": 171
  }
}
