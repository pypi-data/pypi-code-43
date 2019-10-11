#
# Report template (Jinja2 format).
#
#
# This file is a part of Typhoon HIL API library.
#
# Typhoon HIL API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import unicode_literals, print_function

REPORT_TEMPLATE = """
{#
    Jinja2 template for test executor html report

    Author: Aleksandar Lakic

    External variables used:
        finished
        tests
        colors
#}
<html>

<head>
    <title>TyphoonHIL test executor report</title>
    {% if not finished %}
    <meta http-equiv="refresh" content="1">
    {% endif %}

    <style type="text/css">

        .central {
            font-family: Arial,"Arial Unicode MS",Helvetica,Sans-Serif !important;
            font-size: 14px;
            line-height: 20px;
            color: #333;
            margin-left: auto;
            margin-right: auto;
            width: 800px;
        }


        .personal {

            margin-top: 50px;

            margin-right: auto;
            margin-right-value: auto;
            margin-right-ltr-source: physical;
            margin-right-rtl-source: physical;

            margin-left: auto;
            margin-left-value: auto;
            margin-left-ltr-source: physical;
            margin-left-rtl-source: physical;
        }

        h3{
            font-weight: 100;
        }

        .personal h3 {
            font-size: 24.5px;
            line-height: 40px;
            margin: 10px 0px;
            font-family: inherit;
            font-weight: 100;
            color: inherit;
            text-rendering: optimizelegibility;
        }

        hr {
            margin: 10px 0px;
            border-right: 0px none;
            border-left: 0px none;
            border-image: none;
            border-width: 1px 0px;
            border-style: solid none;
            border-color: #EEE;
        }

        .span_info1 {
            font-size: 14px;
            width: 170px;
            margin-left: 30px;
            margin-left-value: 30px;
            margin-left-ltr-source: physical;
            margin-left-rtl-source: physical;
            float: left;
        }

        .span_info2 {
            font-size: 14px;
            width: 600px;
            margin-left: 30px;
            margin-left-value: 30px;
            margin-left-ltr-source: physical;
            margin-left-rtl-source: physical;

        }

        table {
            *border-collapse: collapse; /* IE7 and lower */
            border-spacing: 0;

        }

        .bordered {
            border: solid #ccc 2px;
            -moz-border-radius: 6px;
            -webkit-border-radius: 6px;
            border-radius: 6px;
            -webkit-box-shadow: 0 1px 1px #ccc;
            -moz-box-shadow: 0 1px 1px #ccc;
            box-shadow: 0 1px 1px #ccc;
        }

        .bordered tr:hover {
            background: #fbf8e9;
            -o-transition: all 0.1s ease-in-out;
            -webkit-transition: all 0.1s ease-in-out;
            -moz-transition: all 0.1s ease-in-out;
            -ms-transition: all 0.1s ease-in-out;
            transition: all 0.1s ease-in-out;
        }

        .bordered td, .bordered th {
            border-left: 1px solid #ccc;
            border-top: 1px solid #ccc;
            padding: 10px;
            text-align: center;
            font-size:14px;
        }

        .bordered th {
            background-color: #dce9f9;
            background-image: -webkit-gradient(linear, left top, left bottom, from(#F5F5F5), to(#EEE));
            background-image: -webkit-linear-gradient(top, #F5F5F5, #EEE);
            background-image:    -moz-linear-gradient(top, #F5F5F5, #EEE);
            background-image:     -ms-linear-gradient(top, #F5F5F5, #EEE);
            background-image:      -o-linear-gradient(top, #F5F5F5, #EEE);
            background-image:         linear-gradient(top, #F5F5F5, #EEE);
            -webkit-box-shadow: 0 1px 0 rgba(255,255,255,.8) inset;
            -moz-box-shadow:0 1px 0 rgba(255,255,255,.8) inset;
            box-shadow: 0 1px 0 rgba(255,255,255,.8) inset;
            border-top: none;
            text-shadow: 0 1px 0 rgba(255,255,255,.5);
        }

        .bordered td:first-child, .bordered th:first-child {
            border-left: none;
        }

        .bordered tbody tr:nth-child(even) {
            background: #f5f5f5;
            -webkit-box-shadow: 0 1px 0 rgba(255,255,255,.8) inset;
            -moz-box-shadow:0 1px 0 rgba(255,255,255,.8) inset;
            box-shadow: 0 1px 0 rgba(255,255,255,.8) inset;
        }

        .bordered th:first-child {
            -moz-border-radius: 6px 0 0 0;
            -webkit-border-radius: 6px 0 0 0;
            border-radius: 6px 0 0 0;
        }

        .bordered th:last-child {
            -moz-border-radius: 0 6px 0 0;
            -webkit-border-radius: 0 6px 0 0;
            border-radius: 0 6px 0 0;
        }

        .bordered th:only-child{
            -moz-border-radius: 6px 6px 0 0;
            -webkit-border-radius: 6px 6px 0 0;
            border-radius: 6px 6px 0 0;
        }

        .bordered tr:last-child td:first-child {
            -moz-border-radius: 0 0 0 6px;
            -webkit-border-radius: 0 0 0 6px;
            border-radius: 0 0 0 6px;
        }

        .bordered tr:last-child td:last-child {
            -moz-border-radius: 0 0 6px 0;
            -webkit-border-radius: 0 0 6px 0;
            border-radius: 0 0 6px 0;
        }

	</style>
</head>

<body>
    <div class="central">
        <div style="width:100%; text-align:center">
            {% if report.logo is not none %}
            <img alt="" align="center" src="data:image/png;base64,{{report.logo}}" />
            {% else %}
            <img alt="" align="center" src="data:image/png;base64,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"/>
            {% endif %}
        </div>
        <div>
            {% if report.title is not none %}
            <h1 class="heading" align="center">{{report.title}}</h1>
            {% else %}
            <h1 class="heading" align="center">Test executor report</h1>
            {% endif %}
            <h3 class="heading" align="center">Tests started on {{time}}</h3>

            {% if report.description is not none %}
            <div class="personal" >
                <h3>Description</h3>
                <hr>
                <span class="span_info2">
                {{report.description}}
                </span><br>
            </div>
            {% endif %}
            <div class="personal" >
                <h3>Tests results</h3>
                <hr>
            </div>
        </div>

        <div align="center">
            <table class="bordered">
                <thead>
                    <tr>
                        <th style="min-width:20px">#</th>
                        <th style="min-width:80px">Test Name</th>
                        <th>Description</th>
                        <th style="min-width:80px">Start time</th>
                        <th style="min-width:80px">Status</th>
                        <th style="min-width:60px">Log</th>
                    </tr>
                </thead>
                <tbody>
                    {% for test in tests %}
                    <tr align="center">
                        <td>{{loop.index}}/{{num_tests}}</td>
                        <td>{{test.name if test.name else ""}}</td>
                        <td>{{test.description if test.description else ""}}</td>
                        <td>{{test.start_time}}</td>
                        <td style="background-color:{{colors[test.status]}}; color:black;">{{test.status}}</td>
                        <td><a href="_logs/test_{{loop.index}}.log" target="_blank">Log file</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>

</html>
"""
