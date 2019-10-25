from musket_core import datasets,genericcsv,coders,image_datasets

@datasets.dataset_provider(origin="train.csv",kind="GenericDataSet")
def getTitanic():
    return genericcsv.GenericCSVDataSet("train.csv",["Sex","Fare","Age","Pclass"],["Survived"],[],
                                        {"Sex":"binary","Fare":"normalized_number","Age":"normalized_number","Pclass":"multi_class","Survived":"binary"},input_groups={"0":["Sex","Fare","Age","Pclass"]})
    
@datasets.dataset_provider(origin="saltExists.csv",kind="BinaryClassificationDataSet")
def getSe():
    return image_datasets.BinaryClassificationDataSet(["images"],"saltExists.csv","ImageId","Class")


@datasets.dataset_provider(origin="train.csv",kind="BinarySegmentationDataSet")
def getSaltTrain():
    return image_datasets.BinarySegmentationDataSet(["images","images"],"salt.csv","id","rle_mask")    