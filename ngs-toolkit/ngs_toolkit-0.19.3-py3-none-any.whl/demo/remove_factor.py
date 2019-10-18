from ngs_toolkit.demo import generate_project

a = generate_project(n_factors=3)
a.normalize()

# inspect
a.unsupervised_analysis(output_prefix="before")

# assuming 'B' is the strongest factor

# remove 'B' without regard for the other factors
m = a.remove_factor_from_matrix(
    factor='B',
    assign=False, save=False)
a.unsupervised_analysis(
    matrix=m,
    output_prefix="after_simple")

# remove 'B' accounting for the other factors
m = a.remove_factor_from_matrix(
    factor='B', covariates=['A', 'C'],
    assign=False, save=False)
a.unsupervised_analysis(
    matrix=m,
    output_prefix="after_covariates")

a.generate_report()
