def test(new_directory):
    #!dp test -m graph.pb -s validation_data
    command = "dir"  # Replace with your command
    output, error = execute_command(command, new_directory)

    if output:
        print("Output:\n", output)
    if error:
        print("Error:\n", error)


if __name__ == '__main__':
    from utils.exec_command import execute_command

    # Step 4.2
    new_directory = r'E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out'
    test(new_directory)