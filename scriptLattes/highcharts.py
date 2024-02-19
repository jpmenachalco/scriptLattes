#!/usr/bin/python
# -*- coding: utf-8 -*-
# filename: highcharts.py
#
# scriptLattes
# Copyright 2013: Cristhian W. Bilhalva
#           2015: Fabio N. Kepler (fabio@kepler.pro.br)
# http://scriptlattes.sourceforge.net/
#
#
# Este programa é um software livre; você pode redistribui-lo e/ou 
# modifica-lo dentro dos termos da Licença Pública Geral GNU como 
# publicada pela Fundação do Software Livre (FSF); na versão 2 da 
# Licença, ou (na sua opinião) qualquer versão.
#
# Este programa é distribuído na esperança que possa ser util, 
# mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
# MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, escreva para a Fundação do Software
# Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#

from string import Template

theme = '''{
   colors: ["#1F77B4", "#118D95", "#8085e9", "#8d4654", "#7798BF", "#aaeeee", "#ff0066", "#eeaaee", "#2b908f", "#90ee7e", "#55BF3B", "#DF5353", "#7798BF", "#aaeeee"],
   chart: {
      backgroundColor: null,
      style: {
         fontFamily: "'Source Sans Pro', 'sans-serif'"
      }
   },
   title: {
      style: {
         color: 'black',
         fontSize: '16px',
         fontWeight: 'bold'
      }
   },
   subtitle: {
      style: {
         color: 'black'
      }
   },
   tooltip: {
      borderWidth: 0
   },
   legend: {
      itemStyle: {
         fontWeight: 'bold',
         fontSize: '13px'
      }
   },
   xAxis: {
      labels: {
         style: {
            color: '#6e6e70'
         }
      }
   },
   yAxis: {
      labels: {
         style: {
            color: '#6e6e70'
         }
      }
   },
   plotOptions: {
      series: {
         shadow: true
      },
      candlestick: {
         lineColor: '#404048'
      },
      map: {
         shadow: false
      }
   },

   // Highstock specific
   navigator: {
      xAxis: {
         gridLineColor: '#D0D0D8'
      }
   },
   rangeSelector: {
      buttonTheme: {
         fill: 'white',
         stroke: '#C0C0C8',
         'stroke-width': 1,
         states: {
            select: {
               fill: '#D0D0D8'
            }
         }
      }
   },
   scrollbar: {
      trackBorderColor: '#C0C0C8'
   },

   // General
   background2: '#E0E0E8'
};
'''


class jscmd(object):
    cmd = ''

    def __init__(self, cmd):
        self.cmd = cmd

    def __str__(self):
        return self.cmd


class jsbool(object):
    value = False

    def __init__(self, v):
        if v:
            self.value = True
        else:
            self.value = False

    def __str__(self):
        return 'true' if self.value else 'false'


class bgcolor(object):
    colorstr = '(Highcharts.theme && Highcharts.theme.legendBackgroundColor || \'#FFFFFF\')'

    def __str__(self):
        return self.colorstr


true = jsbool(True)
false = jsbool(False)


def format_json(d):
    s = ''
    # FIXME: juntar as duas lógicas abaixo
    if isinstance(d, list):
        s += '['
        for k in d:
            if isinstance(k, dict):
                s += format_json(k)
            elif isinstance(k, list):
                s += format_json(k)
            elif isinstance(k, str) or isinstance(k, str):
                s += '\'' + k + '\''
            elif k is None:  # we explicitly want None
                s += 'null'
            else:
                s += str(k)
            s += ',\n'
        s = s.rpartition(',')[0]  # tira a vírgula após o último elemento # FIXME: usar join
        s += ']'
    elif isinstance(d, dict):
        s += '{' #if isinstance(d, dict) else '[\n'
        keys = list(d.keys()) #if isinstance(d, dict)
        for k in keys:
            s += (', \n' if k != keys[0] else '') + str(k) + ': '
            if isinstance(d[k], dict):
                s += format_json(d[k])
            elif isinstance(d[k], list):
                s += format_json(d[k])
            elif isinstance(d[k], str) or isinstance(d[k], str):
                s += '\'' + d[k] + '\''
            elif d[k] is None:  # we explicitly want None
                s += 'null'
            else:
                s += str(d[k])
        s += '}' #if isinstance(d, dict) else ']'
    # s += '\n'
    return s


class chart_type(object):
    line = 'line'
    spline = 'spline'
    area = 'area'
    areaspline = 'areaspline'
    column = 'column'
    bar = 'bar'
    pie = 'pie'
    scatter = 'scatter'
    gauge = 'gauge'
    arearange = 'arearange'
    areasplinerange = 'areasplinerange'
    columnrange = 'columnrange'


cmd_event = Template('''function(event){
            dv = document.getElementById("dv-year-"+this.name);
            dv.style.display = '$display';
        }''')


jsondata = {
    'chart': {
        'type': chart_type.bar,
        'height': 400
    },
    'title': {
        'text': ''
    },
    'subtitle': {
        'text': ''
    },
    'xAxis': {
        'title': {
            'text': ''
        }
    },
    'yAxis': {
        'min': 0,
        'title': {
            'text': '',
            'align': 'middle'
        },
        'labels': {
            'overflow': 'justify'
        },
        'stackLabels': {
            'enabled': true,
            'format': '{stack}',
            # 'formatter': jscmd('''function() {
            #         return  this.stack;
            #     }''')
            # 'style': {
            #     'fontWeight': 'bold',
            #     'color': "(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"
            # }
        }
    },
    'tooltip': {
        'enabled': true,
        'valueSuffix': '',
        'shared': false,
        'headerFormat': '<span style="font-size: 10px">{point.key}{point.stack}{series.stack}</span><br/>',
        'pointFormat': '<span style="color:{series.color}">\\u25CF</span> {series.name}: <b>{point.y}</b><br/>',
        # 'footerFormat': 'verbatim',
        # 'formatter': jscmd('''function() {
        #     return '<span style="fill:{this.series.color}">\u25CF</span>' +
        #         "<b>" + this.x + "</b><br/>" +
        #         this.series.name + ":-- " + this.y + "<br/>" +
        #         "Total: " + this.point.stackTotal;
        #     }''')
    },
    'plotOptions': {
        'bar': {
            'dataLabels': {
                'enabled': false
            }
        },
        'column': {
            'stacking': None,
            # 'dataLabels': {
                # 'enabled': 'false',
                # 'color': "(Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'",
                # 'style': {
                #     'textShadow': '0 0 3px black'
                # }
            # }
        },
        'series': {
            'shadow': 'true',
            # FIXME: consertar para que publicações sejam ocultadas da lista (difícil)
            # 'events': {
            #     'show': jscmd(cmd_event.substitute(display='block')),
            #     'hide': jscmd(cmd_event.substitute(display='none'))
            # }
        }
    },
    'legend': {
        'enabled': true,
        'layout': 'vertical',
        'align': 'right',
        'verticalAlign': 'middle',
        # 'x': 40,
        # 'y': 40,
        # 'floating': true,
        'borderWidth': 1,
        'backgroundColor': bgcolor(),
        'shadow': true,
        # 'labelFormatter': jscmd('''function () {
        #         return this.options.stack + ' (click to hide)';
        #     }'''),
    },
    'credits': {
        'enabled': false
    },
    'series': []
}

class highchart(dict):
    htmldata = '''
        <script type="text/javascript" src="./js/jquery.min.js"></script>
        <!--
        <script type="text/javascript" src="./highcharts.js"></script>
        <script type="text/javascript" src="./exporting.js"></script>
        <script type="text/javascript" src="./drilldown.js"></script>
        -->

        <script src="https://code.highcharts.com/highcharts.js"></script>
        <script src="https://code.highcharts.com/modules/drilldown.js"></script>
        <script src="https://code.highcharts.com/modules/exporting.js"></script>

        <script type="text/javascript">
        // Load the fonts
        Highcharts.createElement('link', {
           href: 'https://fonts.googleapis.com/css?family=Source+Sans+Pro:400,700',
           rel: 'stylesheet',
           type: 'text/css'
        }, null, document.getElementsByTagName('head')[0]);

        Highcharts.theme = @theme@
        Highcharts.setOptions(Highcharts.theme);
        $(function () {
            $('#container').highcharts(@jsondata@);
        });
        </script>
        '''

    html = htmldata

    def __init__(self, type=chart_type.bar):
        dict.__init__(self, jsondata)
        self.set_chart_type(type)

    def settitle(self, title):
        self['title']['text'] = title

    def set_x_title(self, title):
        self['xAxis']['title']['text'] = title

    def set_y_title(self, title):
        self['yAxis']['title']['text'] = title

    def set_x_categories(self, categories):
        self['xAxis']['categories'] = categories

    def set_chart_type(self, chartt):
        self['chart']['type'] = chartt

    def set_series(self, series):
        # keys = lista.keys()
        # keys.sort()
        # data = []
        # for k in keys:
        #     qtd = len(lista[k])
        #     if qtd > 0:
        #         s = {'name': k, 'data': [qtd], 'y': [qtd]}
        #         data.append(s)
        # series = [{'name': 'Produções', 'data': data,
        #            'colorByPoint': 'true'}]
        self['series'] = series

    def html(self):
        return self.htmldata.replace('@jsondata@', format_json(self)).replace('@theme@', theme)

    def json(self):
        return format_json(self)

