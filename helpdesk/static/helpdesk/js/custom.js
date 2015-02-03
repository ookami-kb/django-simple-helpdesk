function syncAnswerLabel() {
    var panel = $("#answer-panel");
    if ($("#id_internal").prop('checked')) {
        panel.removeClass('panel-info').addClass('panel-default');
    } else {
        panel.removeClass('panel-default').addClass('panel-info');
    }
}

$(document).ready(function() {
    $("#id_internal").on('change', syncAnswerLabel);
    syncAnswerLabel();
});