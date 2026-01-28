```markdown
![Figure 1: The Transformer - model architecture.](image)

Figure 1: The Transformer - model architecture.

The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder, shown in the left and right halves of Figure 1, respectively.

## 3.1 Encoder and Decoder Stacks

**Encoder:** The encoder is composed of a stack of $N = 6$ identical layers. Each layer has two sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, position-wise fully connected feed-forward network. We employ a residual connection [11] around each of the two sub-layers, followed by layer normalization [1]. That is, the output of each sub-layer is $\text{LayerNorm}(x + \text{Sublayer}(x))$, where $\text{Sublayer}(x)$ is the function implemented by the sub-layer itself. To facilitate these residual connections, all sub-layers in the model, as well as the embedding layers, produce outputs of dimension $d_{\text{model}} = 512$.

**Decoder:** The decoder is also composed of a stack of $N = 6$ identical layers. In addition to the two sub-layers in each encoder layer, the decoder inserts a third sub-layer, which performs multi-head attention over the output of the encoder stack. Similar to the encoder, we employ residual connections around each of the sub-layers, followed by layer normalization. We also modify the self-attention sub-layer in the decoder stack to prevent positions from attending to subsequent positions. This masking, combined with fact that the output embeddings are offset by one position, ensures that the predictions for position $i$ can depend only on the known outputs at positions less than $i$.

## 3.2 Attention

An attention function can be described as mapping a query and a set of key-value pairs to an output, where the query, keys, values, and output are all vectors. The output is computed as a weighted sum

```

**Visual Description:**

*Type:* Architecture diagram (block diagram)

*Main Subject:* The overall structure of the Transformer model, showing its encoder and decoder stacks.

*Key Elements:*
- The diagram is divided into two main vertical sections: the **Encoder** (left) and the **Decoder** (right).
- Both sections are labeled "Nx", indicating they are composed of N identical layers (N=6 as stated in the text).
- **Encoder Stack (Left):**
  - Input flows from bottom to top.
  - Starts with "Input Embedding" (pink box) and "Positional Encoding" (circular icon with sine wave).
  - Feeds into a stack of identical layers.
  - Each layer contains:
    - "Multi-Head Attention" (orange box).
    - "Add & Norm" (grey box) — represents residual connection + layer normalization.
    - "Feed Forward" (blue box).
    - Another "Add & Norm" (grey box).
- **Decoder Stack (Right):**
  - Input flows from bottom to top.
  - Starts with "Output Embedding (shifted right)" (pink box) and "Positional Encoding" (circular icon with sine wave).
  - Feeds into a stack of identical layers.
  - Each layer contains three sub-layers:
    - "Masked Multi-Head Attention" (orange box) — masked to prevent attending to future positions.
    - "Add & Norm" (grey box).
    - "Multi-Head Attention" (orange box) — attends to the encoder's output.
    - "Add & Norm" (grey box).
    - "Feed Forward" (blue box).
    - Final "Add & Norm" (grey box).
- **Final Output:**
  - The top of the decoder stack connects to a "Linear" layer (grey box), then a "Softmax" layer (green box), producing "Output Probabilities".

*Connections & Flow:*
- Arrows indicate the direction of data flow (bottom to top within each stack).
- The encoder's final output (implicitly from its top layer) is fed as key-value input to the second multi-head attention layer in each decoder layer.
- The "Add & Norm" blocks show residual connections (addition of input to sublayer output) followed by normalization.

*Color Coding:*
- Pink: Embedding layers.
- Orange: Attention mechanisms (Multi-Head Attention, Masked Multi-Head Attention).
- Blue: Feed-Forward networks.
- Grey: Add & Norm (residual + normalization) and Linear layer.
- Green: Softmax output layer.
- Circular icons: Positional Encoding.

*Context:*
- This diagram visually represents the core innovation of the Transformer: replacing recurrent or convolutional layers with self-attention mechanisms and feed-forward networks, stacked in encoder and decoder blocks.
- The "Nx" notation emphasizes the repetitive nature of the architecture.
- The diagram highlights the critical components mentioned in the text: self-attention, feed-forward networks, residual connections, layer normalization, and the masking mechanism in the decoder.
```

