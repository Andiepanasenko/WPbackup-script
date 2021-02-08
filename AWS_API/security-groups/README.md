## Get security groups structure

1. Add AWS keys to `Dockerfile`.

2. Build and run:
```bash
docker build .
docker run --rm
```

3. Copy all data from `./aws-sec-group.json` and paste to [json2html.varunmalhotra.xyz/](http://json2html.varunmalhotra.xyz/)

4. Choose `Advanced table formatting`, click "Send".

5. Save page to computer

6. Remove all uselles html-data (such as right column, comments and footer)

7. Save to PDF.

8. Send to PDFiller for edit.
