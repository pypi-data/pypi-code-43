from edc_lab import AliquotType, pl, bc, serum, wb

fbc = AliquotType(name="FBC", alpha_code="FBC", numeric_code="63")

wb.add_derivatives(bc, pl, serum, fbc, wb)
