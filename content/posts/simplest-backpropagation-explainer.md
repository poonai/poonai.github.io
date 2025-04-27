---
title: "Simplest backpropagation explainer"
date: 2025-04-27T14:27:16+05:30
draft: false
---

Neural Networks learn to predict by backpropagation. This article aims to help you, build a solid intuition about the concept using a simple example. The ideas we learn here can be expanded for bigger nerual 
network. I assume that you already know how feed forward neural network works. 

Before reading the article further, take a pen and paper. The calculation used in this article can be done in the head. But I still want you do by hand. 

>> "Mathematics is not a spectator sport." — George Pólya

## Calculus: The Art of Change :

Derivation is used throughout the backpropogation, so it's crucial for us to revise calculus before reaching our desired goal.  As title suggests, derivation is used to find how change in value of an variable affect the result. In the context of neural network, how change in weights affects the results of neural networks. 


Let's look at a simple equation:

\[
y = x^3
\]

If we plug in \(x = 2\), we get:

\[
y = 2^3 = 8
\]

Now, what happens if we slightly increase \(x\) by \(0.01\)? Instead of calculating everything again, we can use the derivative.

The derivative of \(y\) is:

\[
\frac{dy}{dx} = 3x^2
\]

\[
dy = 3x^2 \times dx
\]

Substituting \(x = 2\) and \(dx = 0.01\):

\[
dy = 3(2)^2 \times 0.01 = 12 \times 0.01 = 0.12
\]

So, if \(x\) increases by \(0.01\), \(y\) should increase by about \(0.12\) which is \(8.12\).

Let's check it:

- At \(x = 2\), \(y = 8\).
- At \(x = 2.01\), plugging into the original equation:

\[
y = (2.01)^3 = 8.120601
\]

The actual change is about \(8.1206\), which is very close to our estimate of \(8.12\).

**Note:** The derivative is a good approximation function for small changes, does not work well with
bigger number. Curious?? plug in \(dx = 0.5\) and see yourself.

## No hidden layer

It almost took two days for me to understand backpropagation clearly.
The idea finally clicked when I removed the hidden layer and made it a simple one-to-one network.
We'll take the same route to build up intuition, and later we can stack hidden layers to play with multiple weights.

{{< figure src="/img/one-one.png" width="600" height="400" alt="one-one-network" class="center" >}}



For this simple network, we'll consider the following parameters:

- Input \( x = 2 \)

- Weight \( w = 4 \)

- Target output \( y = 10 \)

The prediction formula is:

\[
\hat{y} = x \times w
\]
Substituting the values:

\[
\hat{y} = 2 \times 4 = 8
\]
Let's define a cost function to determine the error rate:

\[
\text{Cost} = \hat{y} - y = (x \times w) - 10
\]
\[
\text{Cost} = (2 \times 4) - 10 = 8 - 10 = -2
\]
When the cost approaches zero, the predicted output correlates closely with the target output.
But in our case, we are off by 2 units. 

## How do we decrease the cost?

Tweaking the weight parameter will reduce the cost.
However, throwing random weights will not help — it's like finding a needle in a haystack.


