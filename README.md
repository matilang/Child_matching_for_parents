## Child_matching_for_parents

### Author
Mateusz Łangowski, mateusz.langowski@otomin.pl

### Admin Actions
- **Print The Number of All Valid Accounts**
  - Command: `python script.py print-all-accounts`
  - Print the total number of valid accounts.
  - Expected output: integer
  
         >python script.py print-all-accounts --login 555123456 --password sASfC1234
         1233333
         
- **Print The Longest Existing Account**
    - Command: `python script.py print-oldest-account`
    - Print information about the account with the longest existence.
    - Expected output: 

            >python script.py print-oldest-account --login 555123456 --password sASfC1234
            name: Boris
	        email_address: boris@gmail.com
	        created_at: 1990-12-12 13:20:00


- **Group Children by Age**
  - Command: `python script.py group-by-age`
  - Group children by age and display relevant information.
  - Expected output: list of rows according to the example, sorted by count - ascending.
  
         >python script.py group-by-age --login 555123456 --password sASfC1234
         age: 12, count: 5
         age: 10, count: 7
- **Create a database**
  - Command: `python script.py create-database`
  - Print the interface which will help you to provide input to the database.
  - Expected output: string
  
         >python script.py create-database --login 555123456 --password sASfC1234
         1. Display Users
         2. Display Children
         3. Display User Children
         4. Add User
         5. Exit
  
         
### User Actions
- **Print Children**
  - Command: `python script.py print-children`
  - Display information about the user's children. Sort children alphabetically by name.
  - Expected output: list of rows containing `<name>, <age>`

         >python script.py print-children --login 555123456 --password sASfC1234
         Adam, 2
         Sally, 12


- **Find Users with Children of Same Age**
  - Command: `python script.py find-similar-children-by-age`
  - Find users with children of the same age as at least one own child, and print the user and all of his children's data. Sort children alphabetically by name.
  - Expected output: list of rows containing `<name-of-parent>,<parents-telephone-number>: <matched-child-name>, <matched-child-age>; <matched-child-name>, <matched-child-age>`
  
         >python script.py find-similar-children-by-age --login 555123456 --password sASfC1234
         Brock, 789543123: Bart, 4; Olive, 2
         John, 432764512: Sally, 2
### About the code
This code is not in the best shape and I know it. I tried to get all the functionalities working and almost got it. 
I know there is a mistake in my phone validation algorithm and a few of them are deleted and a few are doubled.
There are many error-handling outputs so the user should understand every time, what went wrong.
There are 3 python files:
* db.py which contains the main database class
* sql.py which contains SQL database class
* script.py contains all the functions and uses 'db.py' and 'sql.py'
