import warnings

try:
    from ._perffuncs import diffusion, diffusion_nonavg, active_transport
except ImportError:
    warnings.warn("Import failed, falling back to Python diffusion function")

    def diffusion(dydt, y0, is_celltype, celltype_neighbors, alpha, n_neighbors):
        for cell, cell_conc in enumerate(y0):
            if is_celltype[cell]:
                diff = 0
                for neighbor in celltype_neighbors[cell]:
                    if neighbor != -1:
                        diff += y0[neighbor] - cell_conc
                dydt[cell] += diff / n_neighbors * alpha
        return dydt

    def diffusion_nonavg(dydt, y0, is_celltype, celltype_neighbors, alpha, n_neighbors):
        for cell, cell_conc in enumerate(y0):
            if is_celltype[cell]:
                diff = 0
                for neighbor in celltype_neighbors[cell]:
                    if neighbor != -1:
                        diff += y0[neighbor] - cell_conc
                dydt[cell] += diff * alpha
        return dydt

    def active_transport(dydt, y0, is_celltype, celltype_neighbors, alpha, n_neighbors):
        for cell, cell_conc in enumerate(y0):
            if is_celltype[cell]:
                for neighbor in celltype_neighbors[cell]:
                    if neighbor != -1:
                        diff = (y0[neighbor] - cell_conc) * alpha
                        if diff < 0:
                            dydt[neighbor] += diff
                            dydt[cell] -= diff
        return dydt
