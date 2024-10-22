class ReturnCode:
    # Return codes
    SUCCESS = 0  # No error
    ERROR_CODE_1 = 1  # Error in step 1
    ERROR_CODE_2 = 2  # Error in step 2
    ERROR_CODE_3 = 3  # Error in step 3
    ERROR_CODE_4 = 4  # Error in step 4

    @staticmethod
    def get_message(code):
        """ Return a message based on the return code """
        messages = {
            ReturnCode.SUCCESS: "No error.",
            ReturnCode.ERROR_CODE_1: "Error occurred in step: processing data from siesta output.",
            ReturnCode.ERROR_CODE_2: "Error occurred in step: processing the script prepare to train.",
            ReturnCode.ERROR_CODE_3: "Error occurred in step: processing to train model and plot error.",
            ReturnCode.ERROR_CODE_4: "Error occurred in step: processing to compress, test and vaild model.",
        }
        return messages.get(code, "Unknown return code.")
