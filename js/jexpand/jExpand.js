(function($){
    $.fn.jExpand = function(){
        var element = this;

        $(element).find("tr:odd").addClass("odd");
        $(element).find("tr:not(.odd)").hide();
        $(element).find("tr:first-child").show();
        $(element).data("opened", false);

        $(element).find("tr.odd").click(function(){

            var currentVis = $(this).data("opened");

            $(element).find("tr.odd").next("tr").hide();
            $(element).find("tr.odd").data("opened", false);

            if(!currentVis)
                $(this).next("tr").show();

            $(this).data("opened", !currentVis);
        });
        
    }    
})(jQuery); 