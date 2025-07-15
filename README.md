# The Woolies Chatbot demo
This repository contains the demo scripts used for the chatbot demonstration during APEX 2025 in Chicago. The core of the demo is a Userscript module, which lets you manipulate the page's DOM, capture user events, and inject JavaScript snippets.

Currently, this script only works with the Woolworths website (http://www.woolworths.com.au). However, it can be adapted for other e‑commerce grocery websites by making a few adjustments:
- Updating the DOM selectors for various elements (e.g., the “Add to Cart” button, product names, etc.)
- Identifying the API endpoint that returns the current contents of the shopping cart

If you're not comfortable diving deep into JavaScript, you can still update the script using GitHub Copilot and well-crafted prompts.

The demo flow is as follows:

1 - Browse the website and add at least three products to your shopping cart.
After adding the third item, the script prompts the customer for additional preferences (e.g., “I have a preference for gluten‑free recipes”).
A hybrid search is triggered, combining your preference (via vector embedding) and the shopping cart contents (via lexical matching).
Elastic returns a list of three recipes, which are displayed to the customer.
Once the customer selects a recipe, both the recipe details and the shopping cart contents are sent to an LLM.
The LLM then provides guidance and additional suggestions (e.g., “You’re missing key ingredients,” “Swap this product for a healthier option,” etc.).

|              |                                                                                 |
|--------------|---------------------------------------------------------------------------------|
| __Title__    | Hybrid search and RAG for Ecommerce platform                                    |
| __Duration__ | 10 minutes max                                                                  |
| __Audience__ | Technical and non-technical                                                     |
| __Personas__ |                                                                                 |
| __Products__ | Search and GenAI capabilities                                                   |
| __Features__ | Hybrid search, vectorization, LLM integration                                   |

## Pre-requisites
- An Elastic Serverless account
- The Violentmonkey (or Tempermonkey, Greasemonkey) extension installed
- An Azure OpenAI inference endpoint configured for completion

## Running the demo
The following steps describe how to build and deploy the demo in your envrionment.

### Configure the script
You need to edit the Userscript module and configure the following variables at the top of the script.
```sh
const AGENT_NAME = "Elastic AI Agent";
const WELCOME_MESSAGE = "Hello I'm your cooking assistant made by Elastic for Woolies.";
const WOOLIES_GET_CART_URL = "https://www.woolworths.com.au/apis/ui/Trolley";
const ELASTIC_RECIPES_SEARCH_URL = "https://sandbox-search-genai-e76ccd.es.us-east-1.aws.elastic.cloud/cooking-recipes/_search";
const COMPLETION_ENDPOINT_URL = "https://sandbox-search-genai-e76ccd.es.us-east-1.aws.elastic.cloud/_inference/completion/azureopenai-completion-63bknfmstid";
const ELASTIC_API_TOKEN = "bWwwem41Y0JnSXpvQ0FRckZwNDU6UkdteVNTSG9DVG9MYmVaamt0RDVYUQ==";
const SEARCH_TOTAL_RESULTS = 3;
const SAVED_CHAT_KEY = 'woolies-chatbot-messages';
const ENABLE_AGENT_LOGGING = true;
 ```
 
## Limitations
Because the web portal and the Grafana Agent Push API endpoint are exposed on different ports, you need to disable CORS protection in your browser.

One way to do it is by starting chrome with the specific flag as shown below:

```sh
open -n -a /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --args --user-data-dir="/tmp/chrome_dev_test" --disable-web-security
```

## TO-DO
- Deploy an ingress controller for avoiding CORS issues