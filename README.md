\# Aster \& Row Reliable RAG Support Agent



A small, reliability-focused AI support agent for the fictional ecommerce company Aster \& Row.



The agent combines retrieval-augmented generation over the supplied Markdown knowledge base with a safe order-lookup tool over the supplied mock order data. The implementation focuses on grounded answers, document precedence, safe abstention, privacy, tool reliability, and multi-turn context.



\## Features



\- Markdown knowledge-base ingestion with front-matter metadata.

\- Heading-level document chunking for retrieval.

\- Semantic retrieval using `all-MiniLM-L6-v2`.

\- Normalized embeddings and cosine-similarity ranking.

\- Authority-aware retrieval that prefers active policy content over legacy/internal content.

\- Source references containing filename and relevant heading.

\- Explicit handling of insufficient information.

\- Detection and surfacing of genuine conflicts between current sources.

\- Safe order lookup using `data/orders.json`.

\- Order ID normalization and validation.

\- No fabricated order status or delivery dates.

\- Cancelled/returned orders do not use stale delivery information.

\- Customer-facing order responses exclude private/internal fields.

\- Multi-turn conversation memory.

\- Protection against instruction-like content retrieved from the knowledge base.

\- Human handoff when the system cannot safely complete a request.

\- Automated regression tests.

\- A visible evaluation runner covering the supplied behavior cases.



\## Architecture



The application is intentionally small and uses a modular Python implementation.



```text

User

&#x20; |

&#x20; v

SupportAgent

&#x20; |

&#x20; +--------------------+

&#x20; |                    |

&#x20; v                    v

Retriever          Order Lookup

&#x20; |                    |

&#x20; v                    v

Knowledge Base      orders.json

&#x20; |

&#x20; v

Relevant passages

&#x20; |

&#x20; v

Grounded response

````



\### Main components



\* `src/agent/agent.py`



&#x20; \* Main support-agent behavior.

&#x20; \* Routing between knowledge questions and order requests.

&#x20; \* Conversation handling.

&#x20; \* Grounding, privacy, conflict, and handoff behavior.



\* `src/agent/retriever.py`



&#x20; \* Semantic retrieval.

&#x20; \* Embedding generation.

&#x20; \* Authority-aware ranking.



\* `src/agent/loader.py`



&#x20; \* Markdown loading.

&#x20; \* Front-matter parsing.

&#x20; \* Heading-based chunking.

&#x20; \* Metadata preservation.



\* `src/agent/orders.py`



&#x20; \* Safe order lookup.

&#x20; \* Order ID normalization.

&#x20; \* Customer-facing sanitization.



\* `src/agent/memory.py`



&#x20; \* Conversation/session context.



\* `src/agent/response.py`



&#x20; \* Structured response representation.



\* `src/agent/sources.py`



&#x20; \* Source formatting and references.



\* `evaluation/run\_cases.py`



&#x20; \* Runs the supplied visible behavior cases.



\* `tests/`



&#x20; \* Automated regression tests.



\## Model and retrieval approach



The implementation uses:



\* Language/model layer: the configured local/transformer model used by the agent.

\* Embeddings: `sentence-transformers` with `all-MiniLM-L6-v2`.

\* Retrieval: normalized embedding similarity using NumPy.

\* Storage: in-memory document chunks and embeddings.

\* Source data: Markdown files under `knowledge-base/`.

\* Order data: `data/orders.json`.



Documents are split by Markdown headings so that retrieval operates on relevant passages rather than sending the entire knowledge base to the model.



Front-matter metadata such as status, document type, and priority is preserved. Active policy documents receive an authority advantage during retrieval, while legacy, superseded, and internal content is down-ranked.



\## Reliability and safety decisions



\### Policy precedence



Current active policy content is preferred over legacy or internal material.



Instruction-like text inside retrieved documents is treated as data, not as instructions to the agent.



For example, the migration-note scenario does not cause the agent to adopt the incorrect 60-day policy or automatically approve a return.



\### Grounding



Company-specific answers are based on retrieved company content rather than general model knowledge.



When the available information is insufficient, the agent explicitly says so rather than inventing a claim.



\### Source conflicts



When current authoritative sources genuinely disagree, the agent does not silently choose one.



For example, the Breeze Tumbler case reports the conflicting dishwasher instructions and recommends the safest interim guidance together with human confirmation.



\### Order safety



The order file is not supplied wholesale to the model.



The application performs an order lookup and exposes only customer-facing information.



The agent:



\* asks for an order ID when one is missing;

\* safely handles unknown order IDs;

\* normalizes harmless formatting differences;

\* uses the current order status as authoritative;

\* does not invent unavailable delivery estimates;

\* avoids stale delivery information for cancelled/returned orders;

\* does not expose email addresses, physical addresses, internal notes, risk scores, or other internal fields.



\### Human handoff



The agent recommends human assistance when:



\* authoritative information conflicts;

\* supplied information is insufficient;

\* an order cannot be found;

\* a requested action is not supported;

\* approval or another unsupported operational action would otherwise be required.



\## Setup



Clone the repository and enter the project directory.



Create and activate a virtual environment:



```powershell

python -m venv .venv

.venv\\Scripts\\Activate.ps1

```



Install dependencies:



```powershell

pip install -r requirements.txt

```



Copy the environment template if required:



```powershell

Copy-Item .env.example .env

```



Do not place real credentials or API keys in the repository.



\## Running the tests



Run the automated regression suite:



```powershell

python -m pytest -q

```



Final regression result during development:



```text

33 passed

```



\## Running the evaluation cases



Run the supplied visible evaluation cases with:



```powershell

python evaluation\\run\_cases.py

```



The runner executes all supplied visible scenarios and prints:



\* case ID;

\* user message;

\* selected action;

\* final answer;

\* source references;

\* whether additional input/handoff is required.



The visible evaluation cases cover:



\* retrieval;

\* multi-source grounding;

\* multi-turn conversation;

\* order lookup;

\* tool reliability;

\* privacy;

\* prompt-injection resistance;

\* abstention;

\* source conflict handling.



\## Evaluation results



\### Automated regression tests



| Result | Count |

| ------ | ----: |

| Passed |    33 |

| Failed |     0 |



Command:



```text

python -m pytest -q

```



\### Visible behavior evaluation



The supplied visible cases were executed using:



```text

python evaluation\\run\_cases.py

```



The resulting behavior covered the expected scenarios including:



\* standard return policy;

\* TrailPlus return policy;

\* damaged final-sale items;

\* Canada shipping and multi-turn follow-up;

\* unsupported international destinations;

\* valid order lookup;

\* missing order ID;

\* cancelled order handling;

\* unknown order handling;

\* unavailable delivery estimate;

\* privacy protection;

\* warranty policy;

\* retrieved prompt-injection content;

\* insufficient product information;

\* conflicting active product guidance.



\### Category coverage



| Category            | Coverage |

| ------------------- | -------- |

| Retrieval           | Yes      |

| Groundedness        | Yes      |

| Tool use            | Yes      |

| Privacy             | Yes      |

| Multi-turn behavior | Yes      |

| Prompt security     | Yes      |

| Abstention          | Yes      |

| Source conflict     | Yes      |



The evaluation runner is intentionally lightweight and prints individual case results rather than hiding behavior behind a single aggregate score.



\## Bug diary



\### Bug 1 — Missing conversation memory initialization



\*\*Reproduction\*\*



Running the automated tests initially produced:



```text

AttributeError: 'SupportAgent' object has no attribute 'memory'

```



Several `handle()` tests failed when `add\_message()` attempted to use `self.memory`.



\*\*Root cause\*\*



The test construction path created a `SupportAgent` without initializing the memory object expected by `add\_message()`.



\*\*Fix\*\*



The agent initialization/construction path was corrected so the memory component is available before handling messages.



\*\*Regression test\*\*



The agent handling tests now cover:



\* policy questions;

\* missing order IDs;

\* valid order lookups;

\* unknown order IDs.



Final regression result:



```text

33 passed

```



\### Bug 2 — Unsafe source precedence



\*\*Reproduction\*\*



A migration-note scenario attempted to instruct the agent to ignore the real return policy and use a 60-day policy.



\*\*Root cause\*\*



Retrieved content could otherwise be treated as instructions rather than untrusted knowledge-base data.



\*\*Fix\*\*



Retrieval ranking and agent behavior were adjusted so active authoritative policy content is preferred and instruction-like retrieved content does not override application behavior.



\*\*Regression scenario\*\*



The `retrieved-prompt-injection` evaluation case verifies that the agent continues to use the 30-day current policy and does not automatically approve the return.



\### Bug 3 — Stale order delivery information



\*\*Reproduction\*\*



A cancelled order contained delivery-related fields that could lead to an incorrect arrival-date response.



\*\*Root cause\*\*



A delivery field should not override the order's current cancellation status.



\*\*Fix\*\*



Order handling treats the current status as authoritative and avoids presenting stale delivery information for cancelled orders.



\*\*Regression scenario\*\*



The `cancelled-order-stale-eta` case verifies that a cancelled order is reported as cancelled and not as still arriving.



\### Additional failure discovered beyond the happy path



The evaluation also exposed the need to handle missing and unavailable data explicitly rather than filling gaps with plausible-looking values.



Examples include:



\* unknown order IDs;

\* shipped orders without delivery estimates;

\* incomplete product-material information;

\* conflicting current product-care instructions.



These cases are handled through safe abstention or human handoff rather than guessing.



\## Observability



The application exposes useful execution information through its structured response/evaluation flow.



During evaluation it is possible to inspect:



\* current user messages;

\* action selection;

\* retrieved sources;

\* final answers;

\* whether additional input is required.



The implementation avoids exposing private order fields in customer-facing responses.



\## Known limitations



This is a take-home implementation rather than a production support platform.



Known limitations include:



1\. The retrieval layer is in-memory and does not use a production vector database.

2\. Embeddings are generated when the knowledge base is loaded rather than maintained in a persistent vector index.

3\. The evaluation runner is intentionally lightweight and primarily provides case-level execution output rather than a sophisticated statistical scoring dashboard.

4\. The mock order system assumes possession of an order ID is sufficient authentication, as allowed by the assignment.

5\. There is no production authentication, user management, deployment infrastructure, analytics dashboard, or persistent conversation store.

6\. The application is designed around the supplied Aster \& Row corpus and mock order data.

7\. Before production, I would add stronger automated evaluation scoring, broader paraphrase testing, persistent observability, authentication, rate limiting, and a production-grade retrieval store.



\## AI coding tools used



AI coding assistance was used during development to help with:



\* understanding the repository requirements;

\* designing the initial application structure;

\* debugging Python test failures;

\* improving retrieval and document-precedence behavior;

\* reasoning about order-tool safety;

\* preparing evaluation scenarios and documentation.



AI-generated suggestions were reviewed and tested rather than accepted blindly.



One example of an incomplete suggestion was an implementation path that assumed a `memory` attribute was initialized on every `SupportAgent` construction path. The automated regression tests exposed the missing initialization with:



```text

AttributeError: 'SupportAgent' object has no attribute 'memory'

```



The issue was then corrected and verified with the final 33-test passing result.



\## Demo



A short demonstration should show:



1\. A knowledge-base question with source citations.

2\. An order lookup such as `ORD-1007`.

3\. A multi-turn conversation such as international shipping followed by a Canada follow-up.

4\. A case where the agent refuses to guess or recommends human assistance.

5\. The evaluation suite running.



Add the final GIF or video to this section before submission.



Example:



```markdown

!\[Aster \& Row support agent demo](demo/demo.gif)

```



If using a video hosted externally, a clickable thumbnail/link can be used instead.



\## Project structure



```text

.

├── README.md

├── .env.example

├── requirements.txt

├── knowledge-base/

│   └── supplied Markdown policies and product content

├── data/

│   ├── orders.json

│   └── orders-data-dictionary.md

├── evaluation/

│   ├── visible-cases.json

│   └── run\_cases.py

├── src/

│   └── agent/

│       ├── agent.py

│       ├── config.py

│       ├── loader.py

│       ├── memory.py

│       ├── models.py

│       ├── orders.py

│       ├── response.py

│       ├── retriever.py

│       └── sources.py

└── tests/

&#x20;   └── automated regression tests



