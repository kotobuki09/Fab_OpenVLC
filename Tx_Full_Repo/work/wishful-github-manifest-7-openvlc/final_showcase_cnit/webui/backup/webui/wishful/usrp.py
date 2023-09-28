from bokeh.models import ColumnDataSource
from bokeh.models import CustomJS
from bokeh.models import FuncTickFormatter
from bokeh.models import Title
from bokeh.plotting import figure


def get_plot(name='spectrogram'):
    data = ColumnDataSource(
        data=dict(spectrogram=[]),
        name=name,
    )
    variables = ColumnDataSource(
        data=dict(fc=[2e9], bw=[20e6], size=[512]),
        name=name + '_vars',
    )
    plot = figure(
        plot_height=300, plot_width=400,
        title="Spectrum Waterfall",
        # tools="crosshair,pan,reset,save,wheel_zoom",
        tools="",
        toolbar_location=None,
        x_range=(0, 1000),
        y_range=(0, 500),
        output_backend="webgl",
    )
    usrp_image = plot.image(
        image='spectrogram',
        source=data,
        x=0, y=0,
        dw=1000, dh=500,
        palette="Viridis256",
    )

    plot.xaxis.axis_label = "Time [sample]"
    plot.yaxis.axis_label = "Frequency [GHz]"
    plot.yaxis[0].formatter = FuncTickFormatter(
        args=dict(conf=variables),
        code="""
        var fc = conf.data.fc[0];
        var bw = conf.data.bw[0];
        var size = conf.data.size[0];
        var result = fc - bw / 2 + (tick + 1) * bw / 500;
        return (result / 1e9).toPrecision(4);
    """)
    usrp_txt = Title(
        text='',
        text_font_size='12px',
        align='right')
    usrp_callback = CustomJS(args=dict(source=usrp_txt), code="""
        var fc = (cb_obj.data.fc[0] / 1e9).toPrecision(4);
        var bw = (cb_obj.data.bw[0] / 1e6).toPrecision(2);
        var size = cb_obj.data.size[0];
        source.text = "Center frequency: " + fc
            + " GHz, Bandwidth: " + bw + " MHz, FFT size: " + size;
    """)
    variables.js_on_change('data', usrp_callback)
    plot.add_layout(usrp_txt, "below")
    return plot
