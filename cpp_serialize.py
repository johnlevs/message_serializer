from cpp_serializer.module_list import module_list


if __name__ == "__main__":
    test = module_list("test", "ICD")
    test.scan_directory("./test")
    test.load_modules()

    test._generate_header_files("./test")
    test._generate_source_files("./test")

