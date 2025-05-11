# GNSS-R-WIND
Global Navigation Satellite System-Reflectometry (GNSS-R) is a relatively new field in remote sensing that uses reflected signals from the Earth is surface to study the state of the surface geophysical parameters under observation. In sea remote sensing, GNSS-R can measure sea height, retrieve sea surface wind speed, and estimate seawater salinity. In this study, the algorithm used cyclone global navigation satellite system (CYGNSS) L1 data for sea surface wind speed retrieval. However, it is difficult to obtain high wind speed retrieval results with low errors in real wind speed retrieval experiments based on GNSS-R techniques. To improve the accuracy in high wind speed states, this paper proposes a model for wind speed classification before regression, called the classification regression (CR) model. Existing methods involve one model retrieving all samples with varying wind speed sizes, which can result in a decrease in retrieval accuracy for high wind speeds. Different wind speeds correspond to different delay Doppler
maps (DDM) with distinct features. In this study, wind speeds were categorized
into high and low based on the magnitude of the inter-class distance using an
ensemble learning method. This study proposes a new model named Multimodal
Transformer (M-Trans) for training at low wind speeds, while a Bagged Tree
(BT) regression model is used for training at high wind speeds. The experimental
results from CYGNSS show that the ensemble learning classification results can
be classified correctly by up to approximately 96.9%. With the help of the classification results, the overall root mean square error (RMSE) of the retrieval can
reach 1.71 m/s in the wind speed range of 0-35 m/s. It is worth noting that the
RMSE under high wind speed conditions can be reduced from 7.05 m/s of the
classic algorithm to 2.73 m/s, and the RMSE is reduced by 60.9%. The RMSE
in correctly classified high wind speed samples is 1.38 m/s, which is up to 83.2%
lower than the traditional model. 

Test for git desktop
