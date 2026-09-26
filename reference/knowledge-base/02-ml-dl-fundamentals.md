# 02: Machine Learning and Deep Learning Fundamentals

> A beginner-friendly guide to the ideas used in Weeks 2 to 4.

**Part of AI Engineering Lab - Developed by Zorost Intelligence AI Lab**

## How to use this guide

Do not try to memorize every term on the first reading. For each idea, ask:

1. What problem does this solve?
2. What does it mean in the ZoroLogistics example?
3. What mistake does it help me avoid?

For **Week 2**, read Section 2 first. It explains the no-leakage rule that matters
when cleaning data and preparing it for future models. The later sections prepare you
for Weeks 3 and 4.

## Why this matters

An AI model learns patterns from examples and then makes predictions on new examples.
The prediction can be wrong. That is normal. AI engineering is the discipline of
measuring how wrong the model is, checking whether the measurement is honest, and
finding where the model fails.

The central rule of this course is:

> Choose a metric, use an honest data split, and investigate the errors.

This applies to ordinary machine-learning models, neural networks, language models,
and agents.

ZoroLogistics will use this discipline to answer two questions:

- **ETA regression:** How many hours will a shipment take?
- **On-time classification:** Is a shipment likely to be late?

## 1. Supervised learning

### What is it?

In supervised learning, the computer learns from examples where the answer is already
known.

Each row has:

- **Features:** information used to make a prediction.
- **Target:** the answer the model should learn to predict.

Example:

| distance_km | weight_kg | weather | target |
|---:|---:|---|---:|
| 800 | 500 | clear | 30 hours |

The features are distance, weight, and weather. The target is transit time.

The model studies many rows and learns a relationship:

```text
features -> model -> prediction
```

### Regression

Regression predicts a number. Examples:

- transit time in hours
- shipment cost in dollars
- package weight in kilograms

The prediction can be any reasonable number. Being wrong means being too high or too
low by some amount.

### Classification

Classification predicts a category. Examples:

- on time or late
- safe or risky
- approved or rejected

Many classifiers first produce a probability. For example:

```text
probability of late = 0.73
```

If the decision threshold is `0.50`, the model labels the shipment as late. Changing
the threshold changes how many cases are flagged.

| Task | What the model predicts | ZoroLogistics example |
|---|---|---|
| Regression | A number | `delay_hours` |
| Classification | A category or class probability | on time / late |

## 2. The data split and the no-leakage rule

This is the most important section for Week 2 and Week 3.

### Why split the data?

Suppose you give a student the questions and answers before an exam. The student may
score perfectly by memorizing the answers, but the score does not prove understanding.

The same thing happens to a model if you evaluate it using rows it already saw during
training. It may memorize the training rows instead of learning a pattern that works
on new rows.

Therefore, separate the data into three parts:

| Set | Purpose | How often you use it |
|---|---|---|
| Train | Teach the model its parameters | Many times |
| Validation | Choose settings and compare versions | Many times, for decisions |
| Test | Give the final honest score | Once, at the end |

Typical proportions are 70/15/15 or 80/10/10. The exact percentages are less
important than keeping the roles separate.

### What is leakage?

**Leakage** means information from the future, the target, or the test set sneaks into
training. The model then gets an unfair advantage and the reported score looks better
than real-world performance.

Ask:

> Would this information really be available at the moment the prediction is made?

If the answer is no, do not use it as a feature.

### Why freight data needs a time-aware split

Shipments happen over time. Weather, holidays, traffic, and carrier performance can
change from month to month.

For ZoroLogistics, use this order:

```text
oldest shipments -> train
next time period  -> validation
newest shipments  -> test
```

Do not randomly mix January and December rows. A random split could put a future
shipment in training and an older shipment in the test set. That lets the model learn
from information that would not have existed when the older shipment was predicted.

Example:

```python
cut1 = "2025-09-01"
cut2 = "2025-11-01"

train = df[df.date < cut1]
val = df[(df.date >= cut1) & (df.date < cut2)]
test = df[df.date >= cut2]
```

This means:

- rows before September go into training;
- September and October go into validation;
- November and later go into testing.

### Three common leakage mistakes

1. **Randomly splitting time-based data.** Fix: split chronologically.
2. **Using the answer to create a feature.** For example, using `actual_arrival` to
   predict whether the shipment was late. Fix: only use information known at dispatch.
3. **Fitting a scaler on all data.** Fix: calculate scaling values on train only, then
   apply them to validation and test.

Duplicate rows can also leak. If the same shipment appears in train and test, the
model may memorize it. Remove duplicates before splitting.

## 3. Metrics: how do we measure a model?

A metric is a number that summarizes model performance. Choose it before choosing a
model, because the right metric depends on the business problem.

### Regression metrics

For one row:

```text
error = prediction - actual value
```

#### MAE: mean absolute error

MAE takes the absolute value of each error, then averages them:

```text
MAE = average(|prediction - actual|)
```

If MAE is 3.2 hours, the model is off by about 3.2 hours per shipment on average.
MAE is easy to explain and is not dominated by a few enormous mistakes.

#### RMSE: root mean squared error

RMSE squares each error, averages the squares, and takes the square root:

```text
RMSE = sqrt(average((prediction - actual)^2))
```

Squaring makes large errors count more:

- MAE describes the typical mistake.
- RMSE reveals whether a few mistakes are unusually large.

For ETA, report both in hours.

### Classification metrics

Imagine the model is trying to find late shipments.

- **True positive (TP):** predicted late, actually late.
- **False positive (FP):** predicted late, actually on time. This is a false alarm.
- **False negative (FN):** predicted on time, actually late. This is a miss.
- **True negative (TN):** predicted on time, actually on time.

#### Accuracy

Accuracy is the fraction of all predictions that are correct. It can be misleading.

If 80% of shipments are on time, a model that always says "on time" gets 80%
accuracy while finding zero late shipments. That is why accuracy is not the headline
metric for this problem.

#### Precision

Of the shipments we flagged as late, how many really were late?

```text
precision = TP / (TP + FP)
```

High precision means few false alarms.

#### Recall

Of the shipments that really were late, how many did we find?

```text
recall = TP / (TP + FN)
```

High recall means few missed late shipments.

#### F1

F1 combines precision and recall. It is useful when both false alarms and misses
matter, especially when the late class is smaller than the on-time class.

For ZoroLogistics:

- ETA: primary metric is MAE in hours; RMSE is the warning metric for large errors.
- On-time detection: primary metric is F1 for the late class; also report precision,
  recall, the threshold, and the confusion matrix.

## 4. Cross-validation

Sometimes there is not much data available. Holding out one validation set may give a
noisy result that depends too much on which rows happened to be held out.

In **k-fold cross-validation**:

1. Divide the training data into `k` groups called folds.
2. Train on `k - 1` folds.
3. Evaluate on the remaining fold.
4. Repeat until every fold has been used for evaluation.
5. Average the scores.

This estimates how stable the model is across different parts of the data.

For time-based data, use time-series cross-validation. Each validation period must
come after its training period. Ordinary shuffled k-fold can leak the future again.

## 5. Feature scaling

Features can use very different units:

```text
distance_km = 2500
weight_tons = 3
```

Some models are affected when one feature has much larger numbers than another.
Scaling puts numerical features on comparable ranges.

### Standardization

Standardization subtracts the mean and divides by the standard deviation. The result
usually has mean 0 and standard deviation 1.

### Min-max normalization

Min-max normalization maps values into a chosen range, often 0 to 1.

### Important rule

Calculate scaling values using **training data only**. Then use those values to
transform validation and test. Otherwise, the test set leaks into training.

Tree models such as random forests and gradient boosting usually do not need scaling
because they split on thresholds in the original units.

## 6. Baselines: start with an obvious answer

A **baseline** is a simple method that gives you a minimum score to beat.

Examples:

- Regression: always predict the training mean or median.
- Time series: predict the last observed value.
- Classification: always predict the majority class.

If a complicated model cannot beat the baseline, the complicated model is not useful.
Always report the model's score and its difference from the baseline.

For ZoroLogistics, a lane-average ETA is a strong baseline because distance explains
much of the travel time. A future deep model must beat that baseline before its extra
complexity is justified.

## 7. Bias, variance, and overfitting

### Underfitting: high bias

The model is too simple. It cannot capture the real pattern.

Signs:

- training performance is poor;
- validation performance is also poor;
- the two scores are close.

Possible fixes: add better features, use a more flexible model, or train longer.

### Overfitting: high variance

The model memorizes training examples, including noise, instead of learning a general
pattern.

Signs:

- training performance is very good;
- validation performance is much worse;
- the gap gets larger during training.

Possible fixes: use more data, reduce model size, use regularization, or stop training
earlier.

### Irreducible error

Some randomness or missing information is part of the real problem. No model can
remove all of it.

Practical rule:

> Read the gap between training and validation first, then read the absolute score.

## 8. Learning curves

A learning curve shows training and validation loss as training continues.

| What you see | Likely meaning | First action |
|---|---|---|
| Both losses high and flat | Underfitting | Add capacity or improve features |
| Training low, validation high, gap growing | Overfitting | Regularize, reduce capacity, or add data |
| Both low and close together | Healthy training | Consider training longer |
| Validation starts rising while training falls | Overfitting has started | Keep the earlier checkpoint |

The gap is often more informative than one final number.

## 9. Neural networks: the basic pieces

A neural network is a group of functions with adjustable numbers called **weights**.
Training changes the weights so predictions become less wrong.

### Tensors

A tensor is a numerical array. In PyTorch, tensors also know their data type and
whether they are on the CPU or a GPU.

Common shapes:

- scalar: one number;
- vector: one list of numbers;
- matrix: rows and columns;
- batch: many examples processed together.

If there are `B` examples and `D` features, the input often has shape `(B, D)`.
Tracking shapes carefully prevents many bugs.

### Linear layer

A linear layer applies:

```text
y = xW + b
```

`x` is the input, `W` is a weight matrix, and `b` is a bias. A single linear layer
can only learn linear relationships.

### Activation function

An activation adds a non-linear step. Without activations, many linear layers placed
one after another would still behave like one linear layer.

- **ReLU:** `max(0, x)`, commonly used in hidden layers.
- **Sigmoid:** converts one value to a number between 0 and 1.
- **Softmax:** converts several scores into probabilities that add to 1.
- **GELU:** a smooth activation often used in transformer networks.

### Loss

The loss is one number describing how wrong the current prediction is.

- MSE is common for regression.
- Binary cross-entropy is common for two-class prediction.
- Cross-entropy is common for multiple classes.

The metric you report and the loss you optimize can be different. For example, you
may optimize MSE but report MAE because MAE is easier for the operations team to
understand.

### Gradients and autograd

A gradient tells us how a small change to a weight would change the loss.

PyTorch's **autograd** records the calculations used to produce the loss. When you
run `loss.backward()`, PyTorch works backward through those calculations and computes
the gradients automatically. You write the forward calculation; PyTorch handles the
derivatives.

### Optimizer

An optimizer uses gradients to change the weights.

- **SGD:** takes a basic step in the direction that reduces loss.
- **Adam:** adapts the step for each parameter.
- **AdamW:** Adam with a clearer form of weight decay; a common default.

The **learning rate** controls how large each update is. Too large can make training
unstable; too small can make training painfully slow.

## 10. The training loop

Most neural-network training follows this pattern:

```python
for xb, yb in loader:
    opt.zero_grad()
    predictions = model(xb)
    loss = loss_fn(predictions, yb)
    loss.backward()
    opt.step()
```

In plain language:

1. Take a batch of inputs `xb` and correct answers `yb`.
2. Clear gradients from the previous update.
3. Ask the model for predictions.
4. Measure the loss.
5. Calculate how each weight contributed to the loss.
6. Update the weights.

This is the engine of learning: forward, measure, backward, update.

## 11. Batching

Training on one row at a time is slow and noisy. Training on the entire dataset at
once can require too much memory.

A **batch** is a small group of rows, often 32 to 256. The model calculates an
approximate gradient from that group and updates its weights.

`DataLoader` prepares these batches. It may shuffle training rows, but do not shuffle
validation or test rows when their order matters. Batching also lets a GPU perform
large matrix operations efficiently.

## 12. Regularization

Regularization reduces overfitting by limiting how freely the model can memorize.

### Dropout

During training, dropout temporarily changes some activations to zero. The model
cannot depend on one particular neuron every time. During evaluation, dropout is
turned off and the full network is used.

### Weight decay

Weight decay encourages weights to remain smaller. Smaller weights often produce a
smoother function that is less likely to fit random noise.

Dropout and weight decay use different mechanisms, so they can be combined. The real
test for overfitting is still the training-versus-validation learning curve.

## 13. The AI engineering loop

The course turns every model into a small engineering experiment:

1. **Choose a metric.** State what success means.
2. **Choose an honest split.** Make sure the evaluation data stays unseen.
3. **Build a baseline.** Know what simple approach you must beat.
4. **Train and evaluate.** Record the exact split and result.
5. **Analyze errors.** Break errors down by carrier, lane, weather, or another useful
   segment.
6. **Fix the largest useful problem.** Add a feature, improve the data, or change the
   model.
7. **Measure again.** Keep the improvement only if the metric supports it.

A metric tells you how well the model performed overall. Error analysis tells you
where it failed and what to try next.

## 14. ZoroLogistics: the future use case

Weeks 3 and 4 use the shipment data from Week 1.

### ETA regression

Goal: predict total transit time or the delay correction in hours.

Possible features known at dispatch include:

- lane distance;
- shipment weight;
- carrier reliability;
- weather at dispatch;
- day of week and month;
- commodity type.

Primary metric: **MAE in hours**. If MAE is 3.2, the ETA is off by about 3.2 hours
on average.

Secondary metric: **RMSE in hours**. If RMSE is much larger than MAE, investigate the
small group of very large misses.

Split: earlier dates for training, the next period for validation, and the newest
period for testing.

### On-time classification

Goal: predict whether a shipment will miss its promised window.

The late class is smaller, so accuracy can hide failure. The headline metric is
**F1 for late shipments**.

The model produces a probability of lateness. A threshold turns that probability into
a decision. A lower threshold catches more late shipments but creates more false
alarms. A higher threshold creates fewer false alarms but misses more late shipments.

Choose the threshold using validation data. Use the test set once, after the threshold
has been chosen.

## Final checklist

Before moving on, you should be able to explain:

- the difference between regression and classification;
- why train, validation, and test data have different jobs;
- why freight data must be split by time;
- what leakage is and how to prevent it;
- why MAE and RMSE are both useful;
- why accuracy is weak for an imbalanced target;
- what a baseline is;
- the difference between underfitting and overfitting;
- what a tensor, loss, gradient, optimizer, and batch are;
- why the course requires a metric and an error analysis.

## Short self-check

1. If a model sees a future shipment during training, what rule was broken?
2. If the average ETA error is 4 hours, which metric might that describe?
3. Why can an always-on-time model have high accuracy but still be useless?
4. What does a widening training/validation gap usually mean?
5. Why must the test set be used only at the end?

Answer these in your own words before opening the Week 3 notebooks.

## Sources

- scikit-learn user guide: https://scikit-learn.org/stable/user_guide.html
- PyTorch documentation: https://pytorch.org/docs/stable/
- pandas documentation: https://pandas.pydata.org/docs/
- Andrew Ng, *The AI Engineering Skills Map*: https://www.deeplearning.ai/the-batch/issue-366
