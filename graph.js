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
	'xaxes': [ { 'tickDecimals': 0, 'tickSize': 1 } ],
	'yaxes': [ { 'min': 0 }, { 'alignTicksWithAxis': 1, 'position': 'right' } ]
};

// Loaded asynchronously.
var library = [];

$(document).ready(function()
{
	$.ajax({
		'url': 'library.json',
		'type': 'GET',
		'dataType': 'json',
		'success': function(response)
		{
			library = response;
			// TODO make top-10 lists for causes & cures
			// TODO support open graph with automatically generated preview image
			// TODO add favicon
			$(window).on('hashchange', function()
			{
				var diagnosis = false;
				var code = location.hash.substring(1);
				if(!code)
					return $('button').click();
				for(i in library)
					if(library[i]['code'] == code)
					{
						diagnosis = library[i];
						break;
					}
				if(!diagnosis)
					return $('button').click();
				$.ajax({
					'url': 'data/' + diagnosis['code'] + '.json',
					'type': 'GET',
					'dataType': 'json',
					'success': function(series)
					{
						data[1] = {
							'data': series,
							'label': diagnosis['code'] + ' - ' + diagnosis['label'],
							'bars': { 'show': true }
						};
						var verb = (diagnosis['rval'] > 0) ? 'causes' : 'cures';
						$('h3').text('Did you know? Glyphosate ' + verb + ' ' + diagnosis['label'].toLowerCase() + '!');
						$('span').text('R = ' + diagnosis['rval'] + ', p <= ' + diagnosis['pval']);
						$.plot('#graph', data, options);
					}
				});
			});
			$('button').click(function(e)
			{
				e.preventDefault();
				diagnosis = library[Math.floor(Math.random() * library.length)];
				location.hash = diagnosis['code'];
			});
			if(!location.hash.substring(1))
				$('button').click();
			else
				$(window).trigger('hashchange');
		}
	});
});
