---
title: "Context Pruning in conversational agents"
date: 2025-09-08T11:12:35Z
draft: false
toc: false
images:
tags: 
  - ai
  - context-engineering
  - llm
  - context-pruning
---

# My Journey to Building Agentic Apps

My childhood dream of having a personal **J.A.R.V.I.S** has come true. The recent advancement in **LLMs (Large Language Models)** made me look at it as everyone. As an industry, we all are figuring out how to build agentic apps *“the right way.”*  

The good news is there is no *“the right way”* yet, and the bad news is the same. Since there is no right way, we are seeing a huge influx of frameworks showing up every day, and I'm skeptical about the practical usage of such frameworks. So, my action plan is to use a minimal framework and borrow concepts from those frameworks to build AI apps.  

---

## Why BAML?

The minimal framework is **BAML**. I've been using BAML for the past couple of months and am delighted with the developer experience it offers.  

It offers **function-style LLM calling**. All you have to do is define your prompt, input, and output format in BAML language. Then BAML generates type-safe functions that take typed input and return typed output. This is like any other function you use every day.  

As you read the blog, you'll understand how easy BAML is — or you can check their [docs](https://docs.boundaryml.com/guide/introduction/what-is-baml) as well.  

---

## Context Engineering

**Context engineering** is an important skill in terms of agentic application building. It is essentially providing the right context to steer the LLM in the right direction. There are several ways to do context engineering.  

However, I want to demonstrate **context pruning** in conversational agents. An agent that does a lot of tool calls will be ideal to demonstrate the technique. So, I built an agent that solves mathematical equations which require to stitch multiple tool results. The source code can be seen [here](https://github.com/poonai/context-trimming-sample)  

**Example:**  
Solve the quadratic equation: `x^2 + 5*x + 6 = 0` and find its derivative.

To answer this question:
- it has to solve an equation with a tool call  
- it has to find a derivative with another tool call  

Basically, the agent has to call two tools sequentially to answer the user query. The agent can be implemented by a single prompt. Here is the respective BAML code and prompt for it:  

```baml
class AgentResponse {
    tools QuandraticSolver  | QuadraticDerivative | QuadraticEvaluator | MessageToUser
}

function MathChat(message_history: string[]) -> AgentResponse {
    client OpenRouter
    prompt #"
        You're a helpful Math AI assistant. You have tools to solve equations related to quadratic 
        equations. The user query could be simple, or complex that requires you to take multiple turns
        between you and tools to resolve the user query.

        Use message_to_user tools to reply or ask clarification questions to the user.

        <CONVERSATION HISTORY>
        {% for message in message_history %}
         {{ message}}  
        {% endfor %}
        </CONVERSATION HISTORY>
       
        {{ctx.output_format}}
    "#
}
```

BAML will generate a type-safe Python function where you can pass `message_history` as input and `AgentResponse` as output.  

**Example:**

```python
from baml_client import b

# Example of using the BAML-generated MathChat function
message_history = [
    "{'role': 'user', 'msg': 'Solve the quadratic equation: x^2 + 5*x + 6 = 0'}"
]

# Call the BAML-generated function
agent_response = b.MathChat(message_history)

# The agent_response will contain a tool call, which could be:
# - QuadraticSolver: To solve the equation
# - QuadraticDerivative: To find the derivative
# - QuadraticEvaluator: To evaluate the equation at a specific value
# - MessageToUser: To respond directly to the user
```

The AI response could be a tool call or a response to the user. The AI responds based on the feedback obtained from the external system. All the interactions are stored in `message_history` and used as context to decide the flow of the conversation.  

```python
def chat(self, user_message: str) -> str:
    # Add user message to history
    self.message_history.append({
        'role': 'user',
        'msg': user_message
    })
    
    while True:
        # Get response from BAML MathChat
        agent_response = b.MathChat([str(message) for message in self.message_history])
        
        # Use the tool and get the response
        tool_response = self.use_tool(agent_response)
               
        # If it's a direct message to the user, return it
        if tool_response['role'] == 'assistant':
            return tool_response['msg']
```

---

## Example Message History

```
User: Solve the quadratic equation: x² + 5x + 6 = 0  
Assistant (PROCESSING): I need to solve this quadratic equation. [Calling `quadratic_solver`]  
Tool: Solved equation: x² + 5x + 6 = 0. Roots: [-3, -2]  
Assistant (COMPLETED): The roots of the quadratic equation x² + 5x + 6 = 0 are x = -3 and x = -2.  

User: Find the derivative of: 2x² + 4x − 6  
Assistant (PROCESSING): I need to find the derivative of this quadratic equation. [Calling `quadratic_derivative`]  
Tool: Derivative of equation: 2x² + 4x − 6. Result: 4x + 4  
Assistant (COMPLETED): The derivative of the quadratic equation 2x² + 4x − 6 is 4x + 4.  
```
---



## Pruning the Context

The interaction between tool and AI is not always needed to answer future user questions. Since the AI response already encapsulates the context in its response, tool-related messages can be removed when irrelevant.  

However, we can’t always prune immediately. The AI might still be clarifying missing information before solving. Intermediate tool-related messages should be removed **only when not relevant anymore**. 

## Clarifying Conversation Example

Sometimes the AI must clarify before solving. Example:

```
User: Integrate this equation  
Assistant (PROCESSING): Sure! Could you provide the equation you want me to integrate?  

User: x² + 3x  
Assistant (PROCESSING): I need to integrate this equation. [Calling `integral_solver`]  
Tool: Equation received: x² + 3x. Integration requires clarification: definite or indefinite?  
Assistant (PROCESSING): Do you want me to compute the definite integral (with limits) or the indefinite integral of x² + 3x?  

User: Indefinite integral  
Assistant (PROCESSING): I need to compute the indefinite integral of this equation. [Calling `integral_solver`]  
Tool: Result of ∫(x² + 3x) dx = (x³)/3 + (3x²)/2 + C  
Assistant (COMPLETED): The indefinite integral of x² + 3x is (x³)/3 + (3x²)/2 + C. 
```
---

## Task Status

When to prune context will be decided based on the current phase of the Agent. It could be in **PROCESSING** phase or **COMPLETED** phase. We'll let the LLM itself tell us by adding the `task_status` flag to `message_to_user` tool calls.  

```baml
enum TaskStatus {
    COMPLETED 
    PROCESSING
}

class MessageToUser {
    type "message_to_user" @description(#"
        DESCRIPTION: MessageToUser is used to respond to the user
    "#)

    response string @description(#"
        The assistant response to the user
    "#)

    task_status TaskStatus
}
```

**Example pruning logic:**

```python
if self.context_trimming and tools.task_status == "COMPLETED":
                
    # Convert message history to string list for BAML function
    message_history_str = [str(message) for message in self.message_history]
                
    # Call SummarizeContext BAML function
    summarized_context = b.SummarizeContext(message_history_str)
                
    # Replace message history with summarized context
    self.message_history = summarized_context
```

---

## Summarization

The pruning logic could be as simple as removing all tool calls, or we can use an LLM to **summarize the context** for us.  

```baml
function SummarizeContext(message_history: string[]) -> string []{
    client OpenRouter
    prompt #"
         Your job is to summarize the user conversation to reduce the token length.
         Ideas to summarize:
         - remove intermediate tool calls and tool responses 
         - summarize the user question and response in concise form

         <EXAMPLE INPUT>
           {'role': 'user', 'msg': 'solve x^2 - 5*x + 6 =0 and find derivative'}  
           {'role': 'assistant', 'msg': 'I need to solve this quadratic equation', 'tool_name': 'quadratic_solver', 'tool_args': {'equation': 'x^2 - 5*x + 6 = 0'}}  
           {'role': 'tool', 'msg': 'Solved equation: x^2 - 5*x + 6 = 0. Roots: [2, 3]', 'tool_name': 'quadratic_solver', 'metadata': {'equation': 'x^2 - 5*x + 6 = 0', 'result': '[2, 3]'}}  
           {'role': 'assistant', 'msg': 'I need to find the derivative of this quadratic equation', 'tool_name': 'quadratic_derivative', 'tool_args': {'equation': 'x^2 - 5*x + 6 = 0'}}  
           {'role': 'tool', 'msg': 'Derivative of equation: x^2 - 5*x + 6 = 0. Result: 2*x - 5', 'tool_name': 'quadratic_derivative', 'metadata': {'equation': 'x^2 - 5*x + 6 = 0', 'result': '2*x - 5'}}
           {'role': 'assistant', 'msg': 'The roots of the equation x^2 - 5*x + 6 = 0 are 2 and 3. The derivative of the equation is 2*x - 5. If you want me to evaluate the equation or the derivative at a specific x value, please let me know.', 'tool_name': 'message_to_user'}    
         </EXAMPLE INPUT>

        <EXAMPLE OUTPUT>
           {'role': 'user', 'msg': 'solve x^2 - 5*x + 6 =0 and find derivative'}  
           {'role': 'assistant', 'msg': 'The roots of the equation x^2 - 5*x + 6 = 0 are 2 and 3. The derivative of the equation is 2*x - 5.', 'tool_name': 'message_to_user'}    
        </EXAMPLE OUTPUT>

        <BAD OUTPUT>
          "User asked to solve x^2 - 5*x + 6 = 0, find its derivative, and the squares of the roots; assistant provided roots (2, 3), derivative (2*x - 5), and squares (4, 9)."
        </BAD OUTPUT>

        <GOOD OUTPUT>
        {'role': 'user', 'msg': 'solve x^2 - 5*x + 6 =0 and find derivative'}
        {'role': 'assistant', 'msg': 'roots (2, 3), derivative (2*x - 5)', 'tool_name': 'message_to_user'} 
        </GOOD OUTPUT>
        
        <INPUT>
        {% for message in message_history %}
         {{ message}}  
        {% endfor %}
        </INPUT>
        {{ctx.output_format}}
    "#
} 
```

---

## Token Usage Comparison

Let's [measure](https://github.com/poonai/context-trimming-sample/blob/main/benchmark.py) the token usage with context pruning and without context pruning.


| Agent Type                          | Input Tokens | Output Tokens |
|-------------------------------------|--------------|---------------|
| **Smart Agent (with context pruning)** | 2333         | 309           |
| **Agent (without context pruning)**   | 4883         | 368           |

The lower value is better. We reduced token usage by **47%** while getting the same output by pruning unnecessary context.

Lesser token has the following advatages:
- less hallucination
- less cost
- less response time


