from hammeroflight.arufunctions import cleanandencode, impute_encode
from hammeroflight.arufunctions import qualityreport, featureselector
from hammeroflight.modelcomparator import reg_comparator, clf_comparator
from hammeroflight.modelfitter import run_regressor, run_classifer, fittingplot, goodness_fit
from hammeroflight.modelfitter import kmeans_kfinder, knn_kfinder
from hammeroflight.forecasting import arima_ordertuner, plot_forecast
__version__ = "1.5"