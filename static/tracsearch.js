$(function() {
    $('button.facet').click(function(evt) {
        var sel = 'input[name="facet_' + this.dataset.facet + '"]';
        if ($(this).hasClass('selected')) {
            $(sel).val('');
        } else {
            $(sel).val(this.dataset.term);
        }
        $('form').submit();
    });
    $('button.search').click(function(evt) {
        $('form').submit();
    });
    var values = [];
    var key = null;
    var max = 0;
    $('#datetime td').each(function() {
        var v = parseInt($(this).html(), 10);
        if (key == null) {
            key = v;
        } else {
            values.push({time: key, value: v});
            key = null;
            max = Math.max(max, v);
        }
    });
    var width = 700;
    var format = d3.time.format('%Y-%m-%d');
    var w = width / values.length,
        h = 30;
    var x = d3.scale.linear()
        .domain([values[0].time, values[values.length - 1].time])
        .range([0, width]);
    var y = d3.scale.linear()
        .domain([0, max])
        .rangeRound([0, h]);

    var chart = d3.select('#datetime svg');
    var zoom = d3.behavior.zoom();
    zoom.on('zoom', function() {
        console.log(this, arguments);
        console.log(d3.event);
        console.log(d3.event.sourceEvent.type);
    });
    var drag = d3.behavior.drag();
    var dragorigin;
    var selection;
    drag.on('dragstart', function() {
        var c = $('#datetime svg').offset();
        dragorigin = d3.event.sourceEvent.clientX - c.left;
        chart.append('rect')
        .attr('id', 'selection');
    });
    drag.on('drag', function() {
        var e = d3.event;
        d3.select('#selection')
        .attr('x', dragorigin)
        .attr('y', 0)
        .attr('width', e.x - dragorigin)
        .attr('height', 30);
    var t = new Date(x.invert(e.x - dragorigin));
    d3.select('#info').text(format(t));
    });
    drag.on('dragend', function() {
        var c = $('#datetime svg').offset();
        var dragend = d3.event.sourceEvent.clientX - c.left;
        var start = x.invert(dragorigin);
        var end = x.invert(dragend);
        console.log(format(new Date(start)), format(new Date(end)));
        $('input[name="start"]').val(start);
        $('input[name="end"]').val(end);
        $('form').submit();
    });
    if ($('input[name="start"]').val() == '') {
        $('#zoom').hide();
    }
    $('#zoom').on('click', function() {
        $('input[name="start"]').val('');
        $('input[name="end"]').val('');
        $('form').submit();
    });

    chart.call(drag);

    chart.selectAll('rect')
        .data(values)
        .enter().append('rect')
        .attr('x', function(d, i) { return x(d.time); })
        .attr('y', function(d) { return h - y(d.value) - .5; })
        .on('mouseover', function(d) {
            var t = new Date(d.time);
            d3.select('#info').text(format(t) + ' : ' + d.value);
        }).on('mouseout', function() {
            d3.select('#info').text('');
        })
    .attr('width', 10)
        .attr('height', function(d) { return y(d.value); });
    chart.append('line')
        .attr('x1', 0)
        .attr('x2', w * values.length)
        .attr('y1', h - .5)
        .attr('y2', h - .5);
});
