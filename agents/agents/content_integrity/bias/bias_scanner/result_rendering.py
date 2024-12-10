from jinja2 import Template

html_template = """<p><strong>Overall Bias:</strong> {{ overall_bias.conclusion }}</p>
{% if sentences|length > 0 %}
<p><strong>Sentences:</strong></p>
<ol style="padding-left: 20px;">
    {% for sentence in sentences %}
    <li style="margin-bottom: 10px;">
        <p><strong>Sentence:</strong> <em>{{ sentence.text }}</em></p>
        <p><strong>Bias Type:</strong> {{ sentence.bias_type }} | <strong>Bias Strength:</strong> {{ sentence.bias_strength }}</p>
        <p><strong>Description:</strong> {{ sentence.bias_description }}</p>
    </li>
    {% endfor %}
</ol>
{% endif %}
"""


def render_result(result: dict):
    return Template(html_template).render(**result)
