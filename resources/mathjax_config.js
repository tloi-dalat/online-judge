window.MathJax = {
    loader: {
        load: ['[tex]/color'],
        paths: {
            mathjax: '/static/mathjax/4.1.2',
            'mathjax-newcm': '[mathjax]/output/chtml/fonts/mathjax-newcm',
            'mathjax-bbm-extension': '[mathjax]/output/chtml/fonts/mathjax-bbm-extension',
            'mathjax-bboldx-extension': '[mathjax]/output/chtml/fonts/mathjax-bboldx-extension',
            'mathjax-dsfont-extension': '[mathjax]/output/chtml/fonts/mathjax-dsfont-extension',
            'mathjax-mhchem-extension': '[mathjax]/output/chtml/fonts/mathjax-mhchem-extension'
        }
    },
    tex: {
        packages: {
            '[+]': ['color']
        },
        inlineMath: [
            ['~', '~'],
            ['\\(', '\\)']
        ]
    },
    options: {
        enableMenu: false
    }
};
