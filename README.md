[![CI](https://github.com/markferry/awardwallet/actions/workflows/ci.yml/badge.svg)](https://github.com/markferry/awardwallet/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/markferry/awardwallet/branch/main/graph/badge.svg)](https://codecov.io/gh/markferry/awardwallet)
[![PyPI](https://img.shields.io/pypi/v/awardwallet.svg)](https://pypi.org/project/awardwallet)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# awardwallet

AwardWallet Account Access API wrapper

Import loyalty point transactions from [AwardWallet](https://awardwallet.com/) using their [Account Access API](https://awardwallet.com/api/account>).

As of 2025 AwardWallet integrates over 460 airline, hotel, shopping and other loyalty programmes.

Source          | <https://github.com/markferry/awardwallet>
:---:           | :---:
PyPI            | `pip install awardwallet`
Releases        | <https://github.com/markferry/awardwallet/releases>

## Setup

Follow the instructions in the [API
documentation](https://awardwallet.com/api/account#introduction) to register
for a free Business account and create an API key.

The API key is restricted to the **allowed IP addresses** you specify in the
Business interface API Settings.

## Usage

```python
from awardwallet import AwardWalletClient
import json

api_key = "your_api_key_here"
client = AwardWalletClient(api_key)

print(json.dumps(client.list_providers(), indent=2, ensure_ascii=False))
```

Alternatively use the built-in tool:

```
awardwallet --api-key $your_api_key_here list_providers
```
