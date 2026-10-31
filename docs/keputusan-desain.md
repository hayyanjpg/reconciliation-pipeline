# Keputusan Desain (ADR ringkas)

## ADR-001: SQLite untuk staging, bukan PostgreSQL

**Konteks:** portofolio harus bisa dijalankan reviewer tanpa setup berat.

**Keputusan:** memakai SQLite untuk staging dan check SQL.

**Alasan:** tidak butuh server, file bisa ikut repo, dan sintaks SQL yang
dipakai (JOIN, GROUP BY, HAVING, view, parameter) tetap relevan untuk
PostgreSQL.

**Konsekuensi:** tidak menguji fitur spesifik PostgreSQL seperti window function
lanjutan atau constraint deferrable. Di produksi, schema yang sama dapat
dipindahkan dengan perubahan kecil.

## ADR-002: Check berbasis file SQL, bukan hardcode Python

**Konteks:** aturan kualitas data perlu mudah diaudit dan ditambah.

**Keputusan:** setiap check adalah satu file `.sql` dengan header metadata.

**Alasan:** aturan bisnis terlihat eksplisit, bisa direview sendiri, dan
ditambahkan tanpa mengubah kode Python.

**Konsekuensi:** butuh parser header sederhana dan konvensi penamaan yang
disiplin.

## ADR-003: Dua dataset (dirty dan clean)

**Konteks:** check yang selalu gagal tidak membuktikan apa pun.

**Keputusan:** menyediakan dataset kotor untuk demonstrasi deteksi dan dataset
bersih untuk uji false positive.

**Alasan:** kualitas pipeline diukur dari dua sisi: mampu menangkap masalah dan
tidak menuduh data yang benar.

**Konsekuensi:** ada dua folder output dan dua kali run di CI.

## ADR-004: Quarantine, bukan auto-delete

**Konteks:** baris bermasalah harus tetap bisa ditelusuri.

**Keputusan:** baris gagal dicatat di `rejected_rows.csv` dan tabel staging,
tidak dihapus diam-diam.

**Alasan:** audit trail dan akar masalah hanya bisa dianalisis jika data asli
masih ada.

**Konsekuensi:** perlu proses pembersihan berkala dan kontrol akses.
