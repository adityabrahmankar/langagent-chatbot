# AGIent Chatbot

The AGIent chatbot is an intelligent assistant built using Flask and OpenAI's GPT-4 and Langchain that aims to answer questions on various topics. The chatbot is equipped with multiple tools, including web search, Wolfram Alpha, Python REPL, Bash, and Wikipedia.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Requirements

- Python 3.6+
- Flask
- OpenAI API key
- Google CSE ID
- Google API key
- SERPAPI API key
- Wolfram Alpha App ID

## Installation

1. Clone the repository: git clone https://github.com/adityabrahmankar/langagent-chatbot.git

2. Navigate to the project directory: cd

3. Install the required python packages:
   pip install -r requirements.txt

4. Setup required environment variables :
   export OPENAI_API_KEY="your_openai_api_key"
export GOOGLE_CSE_ID="your_google_cse_id"
export GOOGLE_API_KEY="your_google_api_key"
export SERPAPI_API_KEY="your_serpapi_api_key"
export WOLFRAM_ALPHA_APPID="your_wolfram_alpha_appid"


## Usage

1. Start the Flask application:
python main.py

2. Open your web browser and navigate to `http://0.0.0.0:8080/` to access the chatbot.

## Contributing

1. Fork the project.
2. Create a new branch for your feature (`git checkout -b feature/your-feature-name`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Create a new pull request.

## License

This project is licensed under the [MIT License](LICENSE).

