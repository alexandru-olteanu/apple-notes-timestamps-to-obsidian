set output to ""
set noteCount to 0

tell application "Notes"
    repeat with n in notes of default account
        set noteTitle to the name of n
        set cDate to the creation date of n
        set mDate to the modification date of n
        
        -- Get the folder path
        set folderPath to ""
        try
            set currentFolder to the container of n
            repeat
                try
                    set folderName to the name of currentFolder
                    if folderName is not "" and folderName is not "Notes" then
                        if folderPath is "" then
                            set folderPath to folderName
                        else
                            set folderPath to folderName & "/" & folderPath
                        end if
                    end if
                    set currentFolder to the container of currentFolder
                on error
                    exit repeat
                end try
            end repeat
        end try
        
        -- If there's a folder path, prepend it to the title
        if folderPath is not "" then
            set noteTitle to folderPath & "/" & noteTitle
        end if

        set output to output & noteTitle & "|{|}|" & (cDate as string) & "|{|}|" & (mDate as string) & "\n"
        
        set noteCount to noteCount + 1
        -- Uncomment the next 3 lines if you want to test for a few notes before full sync
        -- if noteCount ³ 10 then
        --     exit repeat
        -- end if
    end repeat
end tell

return output
