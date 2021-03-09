## 3/8
Test acc:
* LSTM
    * Hidden size 8 < 32 = 128
    * Embedding dim 128 < 8 = 32
    * Num layers 1 < 3
    * Outer output dim 8 < 32
* GRU
    * Hidden size 8 = 128 < 32
    * Embedding dim 128 < 8 = 32
    * Num layers 3 <= 1
    * Outer output dim 32 <= 8
* On average LSTM < GRU, LSTM much more sensitive to hyperparams, best LSTM > best GRU.
* Overall, not much of a range. Very similar accuracy curves across 
* TODO: fix orientation feature, check red zone and goal line accuracy to make sure LoS is being used (these should be high), try transformer model, data aug
