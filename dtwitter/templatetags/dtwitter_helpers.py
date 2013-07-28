from django import template

register = template.Library()

@register.simple_tag
def render_dtwitter_js():
    return """
        <script type="text/javascript">
        var twitter_callback = function(){};
        function dtwitter_signin(cb) {
            var width = 800;
            var height = 400;
            var left = (screen.width  - width)/2;
            var _top = (screen.height - height)/2;
            var window_position = 'width='+width+', height='+height+', left='+left+', top='+_top;

            window.open('/twitter/connect/', 'twitter_window', window_position);
            twitter_callback = cb;
            return false;
        }
        </script>
    """
