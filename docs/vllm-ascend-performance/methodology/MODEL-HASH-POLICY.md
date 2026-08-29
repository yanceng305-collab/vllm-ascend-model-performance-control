# Model Download and Hash Policy

## `DOWNLOAD_IN_PROGRESS`

When model files are still arriving, do not hash large weight files, do not create a formal weight identity hash, and do not issue a model compatibility verdict. Record only lightweight directory/file status and keep Stage 0B deferred.

## `MODEL_DOWNLOAD_COMPLETE`

After completion is verified, Stage 0B may hash `config.json`, tokenizer/config identity files, and model/safetensors index files, and publish a reusable weight-file manifest containing filename, size, and relevant mtime. Full weight-file SHA-256 is optional and requires an explicit completion-task rationale because it may be expensive. Do not repeat unchanged full hashes in later stages.

Never treat a hash computed while a weight file is being written as formal provenance.
