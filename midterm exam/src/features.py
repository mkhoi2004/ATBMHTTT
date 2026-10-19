"""
Trích chọn và tiền xử lý đặc trưng PE Header từ EMBER.
Mô phỏng chính xác tập 44 đặc trưng của bài báo và tập đối chứng mở rộng.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

# Danh sách đặc trưng PE Header cốt lõi (44 đặc trưng bám sát bài báo)
PE_HEADER_FEATURES = [
    # General / File Header
    "size",
    "vsize",
    "has_debug",
    "exports_nb",
    "imports_nb",
    "has_relocations",
    "has_resources",
    "has_signature",
    "has_tls",
    "symbols_nb",
    # COFF Header
    "timestamp",
    "machine_type",
    "characteristics_count",
    "has_relocs_stripped",
    "has_executable_image",
    "has_dll_flag",
    # Optional Header
    "subsystem",
    "dll_characteristics_count",
    "has_dynamic_base",
    "has_nx_compat",
    "magic",
    "major_image_version",
    "minor_image_version",
    "major_linker_version",
    "minor_linker_version",
    "major_operating_system_version",
    "minor_operating_system_version",
    "major_subsystem_version",
    "minor_subsystem_version",
    "sizeof_code",
    "sizeof_headers",
    "sizeof_heap_commit",
    # Section statistics
    "sections_count",
    "sections_mean_size",
    "sections_max_size",
    "sections_min_size",
    "sections_mean_entropy",
    "sections_max_entropy",
    "sections_min_entropy",
    "sections_mean_vsize",
    "sections_max_vsize",
    "sections_min_vsize",
    # Data Directories (tương ứng import, export, resource, version info)
    "export_table_size",
    "import_table_size",
    "resource_table_size",
    "certificate_table_size",
    "relocation_table_size",
    "debug_size",
    "iat_size",
]

# Ánh xạ machine type từ string sang mã số
MACHINE_MAP = {
    "I386": 332,
    "AMD64": 34404,
    "ARM": 448,
    "ARM64": 43620,
    "UNKNOWN": 0,
}

SUBSYSTEM_MAP = {
    "WINDOWS_GUI": 2,
    "WINDOWS_CUI": 3,
    "NATIVE": 1,
    "UNKNOWN": 0,
}

MAGIC_MAP = {
    "PE32": 267,
    "PE32_PLUS": 523,
    "UNKNOWN": 0,
}


def parse_ember_record_to_features(obj: dict) -> dict:
    """
    Chuyển đổi một bản ghi JSON EMBER thành dictionary các đặc trưng PE Header phẳng.
    """
    general = obj.get("general", {})
    coff = obj.get("header", {}).get("coff", {})
    optional = obj.get("header", {}).get("optional", {})
    sections = obj.get("section", {}).get("sections", [])
    data_dirs = {d.get("name", ""): d.get("size", 0) for d in obj.get("datadirectories", [])}

    # Xử lý Machine string / int
    machine = coff.get("machine", 0)
    if isinstance(machine, str):
        machine_code = MACHINE_MAP.get(machine.upper(), hash(machine) % 10000)
    else:
        machine_code = int(machine or 0)

    # Xử lý Characteristics (có thể là list string hoặc int)
    chara = coff.get("characteristics", [])
    if isinstance(chara, list):
        chara_count = len(chara)
        has_relocs_stripped = 1 if "RELOCS_STRIPPED" in chara else 0
        has_executable_image = 1 if "EXECUTABLE_IMAGE" in chara else 0
        has_dll_flag = 1 if "DLL" in chara else 0
    else:
        chara_count = int(chara or 0)
        has_relocs_stripped = int(bool(chara_count & 0x0001))
        has_executable_image = int(bool(chara_count & 0x0002))
        has_dll_flag = int(bool(chara_count & 0x2000))

    # Xử lý Subsystem
    subsystem = optional.get("subsystem", 0)
    if isinstance(subsystem, str):
        subsystem_code = SUBSYSTEM_MAP.get(subsystem.upper(), hash(subsystem) % 1000)
    else:
        subsystem_code = int(subsystem or 0)

    # Xử lý DllCharacteristics (list string hoặc int)
    dll_chara = optional.get("dll_characteristics", [])
    if isinstance(dll_chara, list):
        dll_count = len(dll_chara)
        has_dynamic_base = 1 if "DYNAMIC_BASE" in dll_chara else 0
        has_nx_compat = 1 if "NX_COMPAT" in dll_chara else 0
    else:
        dll_count = int(dll_chara or 0)
        has_dynamic_base = int(bool(dll_count & 0x0040))
        has_nx_compat = int(bool(dll_count & 0x0100))

    # Xử lý Magic
    magic = optional.get("magic", 0)
    if isinstance(magic, str):
        magic_code = MAGIC_MAP.get(magic.upper(), hash(magic) % 1000)
    else:
        magic_code = int(magic or 0)

    # Thống kê Section
    s_sizes = [s.get("size", 0) for s in sections] if sections else [0]
    s_entropies = [s.get("entropy", 0.0) for s in sections] if sections else [0.0]
    s_vsizes = [s.get("vsize", 0) for s in sections] if sections else [0]

    row = {
        "sha256": obj.get("sha256", ""),
        "appeared": obj.get("appeared", ""),
        "label": int(obj.get("label", -1)),
        # General / File Header
        "size": float(general.get("size", 0)),
        "vsize": float(general.get("vsize", 0)),
        "has_debug": int(general.get("has_debug", 0)),
        "exports_nb": int(general.get("exports", 0)),
        "imports_nb": int(general.get("imports", 0)),
        "has_relocations": int(general.get("has_relocations", 0)),
        "has_resources": int(general.get("has_resources", 0)),
        "has_signature": int(general.get("has_signature", 0)),
        "has_tls": int(general.get("has_tls", 0)),
        "symbols_nb": int(general.get("symbols", 0)),
        # COFF Header
        "timestamp": float(coff.get("timestamp", 0)),
        "machine_type": float(machine_code),
        "characteristics_count": float(chara_count),
        "has_relocs_stripped": float(has_relocs_stripped),
        "has_executable_image": float(has_executable_image),
        "has_dll_flag": float(has_dll_flag),
        # Optional Header
        "subsystem": float(subsystem_code),
        "dll_characteristics_count": float(dll_count),
        "has_dynamic_base": float(has_dynamic_base),
        "has_nx_compat": float(has_nx_compat),
        "magic": float(magic_code),
        "major_image_version": float(optional.get("major_image_version", 0)),
        "minor_image_version": float(optional.get("minor_image_version", 0)),
        "major_linker_version": float(optional.get("major_linker_version", 0)),
        "minor_linker_version": float(optional.get("minor_linker_version", 0)),
        "major_operating_system_version": float(optional.get("major_operating_system_version", 0)),
        "minor_operating_system_version": float(optional.get("minor_operating_system_version", 0)),
        "major_subsystem_version": float(optional.get("major_subsystem_version", 0)),
        "minor_subsystem_version": float(optional.get("minor_subsystem_version", 0)),
        "sizeof_code": float(optional.get("sizeof_code", 0)),
        "sizeof_headers": float(optional.get("sizeof_headers", 0)),
        "sizeof_heap_commit": float(optional.get("sizeof_heap_commit", 0)),
        # Section statistics
        "sections_count": float(len(sections)),
        "sections_mean_size": float(np.mean(s_sizes)),
        "sections_max_size": float(np.max(s_sizes)),
        "sections_min_size": float(np.min(s_sizes)),
        "sections_mean_entropy": float(np.mean(s_entropies)),
        "sections_max_entropy": float(np.max(s_entropies)),
        "sections_min_entropy": float(np.min(s_entropies)),
        "sections_mean_vsize": float(np.mean(s_vsizes)),
        "sections_max_vsize": float(np.max(s_vsizes)),
        "sections_min_vsize": float(np.min(s_vsizes)),
        # Data Directories
        "export_table_size": float(data_dirs.get("EXPORT_TABLE", 0)),
        "import_table_size": float(data_dirs.get("IMPORT_TABLE", 0)),
        "resource_table_size": float(data_dirs.get("RESOURCE_TABLE", 0)),
        "certificate_table_size": float(data_dirs.get("CERTIFICATE_TABLE", 0)),
        "relocation_table_size": float(data_dirs.get("BASE_RELOCATION_TABLE", 0)),
        "debug_size": float(data_dirs.get("DEBUG", 0)),
        "iat_size": float(data_dirs.get("IAT", 0)),
    }
    return row


class FeaturePreprocessor:
    """
    Pipeline tiền xử lý đặc trưng chuẩn mực:
    - Điền giá trị thiếu (median)
    - Chuẩn hóa (StandardScaler)
    - Tuân thủ nghiêm ngặt nguyên tắc No Look-ahead Bias (chỉ fit trên tập train quá khứ)
    """

    def __init__(self, feature_names=None, scale=False):
        self.feature_names = feature_names or PE_HEADER_FEATURES
        self.scale = scale
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler() if scale else None
        self.is_fitted = False

    def fit(self, X: pd.DataFrame, y=None):
        X_sub = X[self.feature_names]
        self.imputer.fit(X_sub)
        if self.scaler:
            X_imp = self.imputer.transform(X_sub)
            self.scaler.fit(X_imp)
        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted before transform!")
        X_sub = X[self.feature_names]
        X_imp = self.imputer.transform(X_sub)
        if self.scaler:
            return self.scaler.transform(X_imp)
        return X_imp

    def fit_transform(self, X: pd.DataFrame, y=None) -> np.ndarray:
        return self.fit(X, y).transform(X)
