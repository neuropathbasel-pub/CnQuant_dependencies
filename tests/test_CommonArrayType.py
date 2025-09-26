from cnquant_dependencies.CommonArrayType import CommonArrayType
from cnquant_dependencies.ArrayType import ArrayType

def test_CommonArrayType():
    all_members_set = set(CommonArrayType.members_list())
    correct_all_members_set = {CommonArrayType.EPIC_v2_to_HM450K, CommonArrayType.EPIC_v2_to_MSA48}
    assert all_members_set == correct_all_members_set, f"members_list() returned {all_members_set}, expected {correct_all_members_set}"
    assert all(True for element in CommonArrayType.get_array_types(CommonArrayType.EPIC_v2_to_HM450K) if element in all_members_set), f"EPIC_v2_to_HM450K contains invalid ArrayType members: {[element for element in CommonArrayType.get_array_types(CommonArrayType.EPIC_v2_to_HM450K) if element not in all_members_set]}"
    assert all(True for element in CommonArrayType.get_array_types(CommonArrayType.EPIC_v2_to_MSA48) if element in all_members_set), f"EPIC_v2_to_MSA48 contains invalid ArrayType members: {[element for element in CommonArrayType.get_array_types(CommonArrayType.EPIC_v2_to_MSA48) if element not in all_members_set]}"
    value_to_key_mapping = CommonArrayType.value_to_key_mapping(common_array_types=[CommonArrayType.EPIC_v2_to_HM450K, CommonArrayType.EPIC_v2_to_MSA48])
    shall_be_mapping = {
        "EPIC_v2_to_HM450K": "EPIC_v2_to_HM450K",
        "EPIC_v2_to_MSA48": "EPIC_v2_to_MSA48"
    }
    assert sorted([value_to_key_mapping.items()]) == sorted([shall_be_mapping.items()]), f"value_to_key_mapping returned {value_to_key_mapping}, expected {shall_be_mapping}"

if __name__ == "__main__":
    test_CommonArrayType()