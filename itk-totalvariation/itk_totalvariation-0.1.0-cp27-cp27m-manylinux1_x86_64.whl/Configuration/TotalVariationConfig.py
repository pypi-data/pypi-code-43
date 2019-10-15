depends = ('ITKPyBase', 'ITKImageSources', 'ITKImageFilterBase', 'ITKCommon', )
templates = (
  ('ProxTVImageFilter', 'itk::ProxTVImageFilter', 'itkProxTVImageFilterIF2IF2', True, 'itk::Image< float,2 >, itk::Image< float,2 >'),
  ('ProxTVImageFilter', 'itk::ProxTVImageFilter', 'itkProxTVImageFilterIF3IF3', True, 'itk::Image< float,3 >, itk::Image< float,3 >'),
)
snake_case_functions = ('prox_tv_image_filter', )
