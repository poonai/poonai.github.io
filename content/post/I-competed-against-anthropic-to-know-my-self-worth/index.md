---
title: "I competed against Anthropic to know my self-worth"
date: "2026-01-31"
draft: false
image: ./whatsapp_invitation.jpeg
tags: 
  - AI
  - optimization
---
The whole ego competition started when I received a text message saying, “Anyone here is trying this?” with a blog title: AI-resistant technical tech evaluation. As I read the blog, I was excited to see how far AI agents have caught up with coding tasks, and it also created a subtle fear in me of not being valuable anymore. I bet some of you have already felt that way at some point. Anthropic’s open challenge to beat Claude seemed like an invitation to test my self-worth.

After the initial glance at the assignment, I was genuinely impressed by the way they designed it. It contains a toy accelerator and a kernel program that needed to be optimized. Interestingly, the toy accelerator comes with tracing and debug functionality. Such level of detail energized me to solve the problem.

### Before we optimize the kernel, let us understand what the kernel does:
```python
def reference_kernel(t: Tree, inp: Input):
    """
    Reference implementation of the kernel.

    A parallel tree traversal where at each node we set
    cur_inp_val = myhash(cur_inp_val ^ node_val)
    and then choose the left branch if cur_inp_val is even.
    If we reach the bottom of the tree we wrap around to the top.
    """
    for h in range(inp.rounds):
        for i in range(len(inp.indices)):
            idx = inp.indices[i]
            val = inp.values[i]
            val = myhash(val ^ t.values[idx])
            idx = 2 * idx + (1 if val % 2 == 0 else 2)
            idx = 0 if idx >= len(t.values) else idx
            inp.values[i] = val
            inp.indices[i] = idx
```

It is a good old binary tree traversal with a twist. Each node is hashed with a value. The evenness of the hash will 
determine the path of the traversal. If the hash is even-valued, the program traverse left; otherwise, it traverse right.
The same traversal logic is replicated for a list of values. Please stare at the above python code to get a cleaner intuition. It is easier to understand code than paragraph.

```python
for round in range(rounds):
    for i in range(batch_size):
        i_const = self.scratch_const(i)
        # idx = mem[inp_indices_p + i]
        body.append(("alu", ("+", tmp_addr, self.scratch["inp_indices_p"], i_const)))
        body.append(("load", ("load", tmp_idx, tmp_addr)))
        body.append(("debug", ("compare", tmp_idx, (round, i, "idx"))))
        # val = mem[inp_values_p + i]
        body.append(("alu", ("+", tmp_addr, self.scratch["inp_values_p"], i_const)))
        body.append(("load", ("load", tmp_val, tmp_addr)))
        body.append(("debug", ("compare", tmp_val, (round, i, "val"))))
        .....
        .....
        # mem[inp_indices_p + i] = idx
        body.append(("alu", ("+", tmp_addr, self.scratch["inp_indices_p"], i_const)))
        body.append(("store", ("store", tmp_addr, tmp_idx)))
        # mem[inp_values_p + i] = val
        body.append(("alu", ("+", tmp_addr, self.scratch["inp_values_p"], i_const)))
        body.append(("store", ("store", tmp_addr, tmp_val)))
```
The provided kernel is an exact reimplementation of the Python code without any vectorization. At this point, I was deluding myself into thinking that vectorization would solve the problem. But I discovered my disappointment only after vectorizing the program. It did not even cut half of the compute cycles.

```python
for i in range(int(batch_size / VLEN)):
    i_const = self.scratch_const(i * VLEN)
    batch_slots(
        "alu",
        ("+", indices_index + i, self.scratch["inp_indices_p"], i_const),
    )
    batch_slots(
        "alu", ("+", value_index + i, self.scratch["inp_values_p"], i_const)
    )
flush_slots()
```

```bash
// Before
{'valu': [('+', 600, 16, 24)]}
{'valu': [('+', 640, 16, 64)]}

// After
{'valu': [('+', 600, 16, 24), ('+', 608, 16, 32),('+', 616, 16, 40), ('+', 624, 16, 48),
('+', 632, 16, 56), ('+', 640, 16, 64)]}
```

The next obvious optimization is to pack multiple independent vectorized operations into one VLIW bundle. VLIW operations are energy efficient and are also a key reason behind Google’s TPU adoption. Essentially, we can batch six operations into one cycle. There were multiple independent operations that can be batched together. One of them is `indices` and `values` offset calculation.

I'm going to take a tiny detour to say something else which is also useful here. I was quietly studying
undergrad math for 8 months without any sort of connection with tech world. I was away from 
Github, Reddit; any sort of connection that would pull me back into the tech echo chamber. At
that time, I noticed something that most of the mathematicians agree. **Many of the problems are
solved by rewriting the problem into a different form;** `a^2-1` can be written as `(a+1)(a-1)`. 
That is your key to optimize further and you can even beat Claude in this game with the
understanding the structure of the tree.

### Starting Line
The interviewing candidates at Anthropic starts at 18532. Because most of the LLM models can figure vectorization at the first pass. Hence, they adjusted the baseline to reflect that.

Now, our compute cycle also would be around
19,000. This marks the official starting line of the game, whatever the cool things we did so 
far were just an warmup.

Revealing the solution would defeat the purpose 
of the assignment. However, the purpose has been already defeated. Some bad actors have released parts or the full solution. You can check that if you want. Best humans have gone beyond Claude's performance. So, decide whether you want to be a mere spectator or the adreline rushed player in the game.

The released version baseline is 1,47,734 cycles. My kernel version took 3,465 cycles and the Claude's best version is at 1,487 cycles, which is 1,978 cycles fewer than mine. That makes the claude version 2.3x faster; This revelation made the protective nature of my ego
to think otherwise.

Before you all close the tab, I want you to watch this [Youtube Shorts](https://www.youtube.com/shorts/1MOzJuDF1cc) that is closely related to this blog context.




