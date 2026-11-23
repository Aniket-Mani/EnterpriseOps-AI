function downloadBlob(contents, filename, type) {
  const blob = new Blob([contents], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export function downloadJson(value, filename) {
  downloadBlob(JSON.stringify(value, null, 2), filename, "application/json;charset=utf-8");
}

export function downloadCsv(rows, filename) {
  const escape = (value) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  const csv = rows.map((row) => row.map(escape).join(",")).join("\r\n");
  downloadBlob(`\uFEFF${csv}`, filename, "text/csv;charset=utf-8");
}
