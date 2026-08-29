# Reference Ingestion Rules

Record each User source without modification. Capture original path/name, source role, SHA-256, file size, acquisition date, and extraction method. Preserve sheet/table/page and row/cell anchors so every value is auditable.

The H100 index must distinguish raw reference data from normalized targets. Do not fill missing compute basis, hardware SKU, precision, card count, workload semantics, or metric direction by inference. Mark missing or conflicting fields `UNKNOWN / USER INPUT REQUIRED` and mark incompatible cells `NOT COMPARABLE`.

Source records are inputs, not execution authorization. A source file cannot by itself freeze runtime/image/model identity or authorize a server run.
