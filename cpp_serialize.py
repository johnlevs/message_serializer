from cpp_serializer.module_list import module_list


if __name__ == "__main__":
    test = module_list("demo", "demoMessages")
    test.scan_directory("demo")
    test.load_modules()

    test._generate_header_files("demo")
    test._generate_source_files("demo")
