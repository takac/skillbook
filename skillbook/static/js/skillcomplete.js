$(function() {
    var cache = {};
    $("#skill-search").autocomplete({
        minLength: 0,
        source: function( request, response ) {
            var term = request.term;
            if ( term in cache ) {
                response( cache[ term ] );
                return;
            }

            $.getJSON( "/skills/json", request, function( data, status, xhr ) {
                data = $.map(data, function(e) {
                    return {
                        label: e.name,
                        id: e.id
                    }
                });
                cache[ term ] = data;
                response( data );
            });
        },
        select: function (event, ui) {
            var v = ui.item.id;
            $('#selected').val(v);
            // $('#Hidden1').html("Something else here" + v);
            // this.value = v; 
            return false;
        }
    });
});
