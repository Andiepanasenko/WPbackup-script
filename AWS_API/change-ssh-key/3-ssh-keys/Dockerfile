FROM python:3.6.5-alpine3.7

LABEL "author"="MaxymVlasov" \
      "email"="vlasov.maksym@pdffiller.team"

WORKDIR /app

COPY escape_ssh_key_for_replace.py /app/

CMD ["python3", "escape_ssh_key_for_replace.py"]
