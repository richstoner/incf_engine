export PORT=$webapp_port
export APP_NAME=$app_name
export SECRET_KEY=$secret_key
export DEBUG=$debug

{% if groups['dbservers']|length > 0 %}
export DATABASE_URL=postgres://$app_name:$database_password@{{ groups['dbservers'][0] }}/$app_name
{% endif %}
