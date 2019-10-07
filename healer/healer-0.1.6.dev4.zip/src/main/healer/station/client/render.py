"""
"""

# __pragma__('jsiter')


class RenderFun:

    bind_input_error = lambda key : {
        'v-bind:state' : f"!validate_error.has('{key}')",
        'v-bind:invalid-feedback' : f"validate_error.first('{key}')",
    }

    bind_error_status = lambda message : {
        'v-bind:state' : f"submit_result()",
        'v-bind:invalid-feedback' : f"'{message}'",
    }

    bind_submit_disable = lambda : {
        'v-bind:disabled' : 'validate_error.any() || !has_input()',
    }

    use_tooltip = lambda text : {
        'title' : text,
        'v-b-tooltip.hover.bottomright':''
    }

    use_width = lambda value = '40ch' : {
        'style' : f'max-width:{value}',
    }

    use_header = lambda variant = 'warning': {
        'header-bg-variant':variant,
        'hide-header-close':'',
    }

# __pragma__('nojsiter')
