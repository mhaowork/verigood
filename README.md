# VeriGood Email Agent

The VeriGood Email Agent is a Python application designed to automate the process of reading verification codes or login links from Gmail using GPT.

## Features

- Fetches new emails automatically. Only Gmail is supported currently.
- Uses OpenAI's GPT model to extract validation codes or links.
- Copies validation codes or links to the clipboard.
- Plays a beepy sound on macOS when a validation code / link is found.


## Prerequisites

Before installing and running this program, ensure you have the following:

- Python 3.10.7 or greater
- Google Gmail API aka Google OAuth Client ID and Secret downloaded as `credentials.json`
  - Follow [this Google guide](https://developers.google.com/gmail/api/quickstart/python) until the `Authorize credentials for a desktop application` step where you will download your `credentials.json`
- OpenAI API
  - Get your OpenAI API key. If you don't know how, check out [this](https://platform.openai.com/docs/quickstart) and [this](https://platform.openai.com/docs/quickstart).

# Installation

1. Download this repo and enter the folder
```bash
git clone https://github.com/mhaowork/verigood
cd verigood
```

2. Move `credentials.json` into the source code's folder.

3. Export your OpenAI API key as an environment variable
```bash
export OPENAI_API_KEY='your-api-key-here'
``` 

4. Start the docker container with docker compose
```bash
docker-compose up
```

5. In the shell, you will be prompted to visit the google oauth URL to authorize the application.

    For example, you will see the following message:
```
Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=xyz....
```


6. Once successful, your Google's auth tokens will be cached in `token.json` under the same folder so the oauth flow will be skipped in the future runs.

7. **Enjoy!**

P.S. If you don't like docker or docker compose for some reason, you can use the application directly by calling `python gmail_agent.py` after installing the dependencies in `requirements.txt`.





