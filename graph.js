var glyphosate = [
	[2012, 14785],
	[2009, 17695],
	[2006, 8215],
	[2004, 5685],
	[2002, 1776],
	[2000, 3200],
	[1998, 2190],
	[1997, 1500],
	[1996, 1421],
	[1995, 199],
//	[1994, 708],
//	[1993, 368],
//	[1992, 111],
//	[1991, 217],
//	[1990, 266],
];

var data = [
	{ 'data': glyphosate, 'label': 'Glyphosate', 'yaxis': 2, 'lines': { 'show': true } },
];

var options = {
	'legend': { 'position': 'nw' },
	'series': { 'stack': true },
	'xaxes': [ { 'tickDecimals': 0, 'tickSize': 1 } ],
	'yaxes': [ { 'min': 0 }, { 'alignTicksWithAxis': 1, 'position': 'right' } ]
};

$(document).ready(function()
{
	$('button').click(function(e)
	{
		e.preventDefault();
		var code = $('input').val();
		if(!code.length)
			code = codes[Math.floor(Math.random() * codes.length)];
		$.ajax({
			'url': 'data/' + code + '.json',
			'type': 'GET',
			'dataType': 'json',
			'success': function(series)
			{
				series['bars'] = { 'show': true }
				data.push(series);
				$('span').text('R = ' + series['rval'] + ', p <= ' + series['pval']);
				$.plot('#graph', data, options);
			}
		});
	});

	$('button').click();
});
