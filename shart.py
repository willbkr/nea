#############################################################################
# Stack class implemented with an array
class Stack:
    # Constructor
    def __init__(self):
        self.StackPointer = -1
        self.Max = 4
        self.Contents = ["" for Elements in range(self.Max)]

    # Add an item to the stack
    def Push(self, Item):
        if self.StackPointer < self.Max - 1: # check for overflow!!!!!!!!!! if not then continue
            self.StackPointer += 1 # go to the next address (pointer plus one!!!!!!!!!)
            self.Contents[self.StackPointer] = Item # Set it!!!!!!!!!!!!!
            return True
        return False
        
        # No lol

    # Remove an item from the stack
    def Pop(self, Item):
        if self.StackPointer == -1: # check for an underflow, is the pointer at the base value doe?!!!!!!!!!!!?!
            return None #shi is empty lmao
        else: #Otherwise 🤓
            Item = self.Contents[self.StackPointer] # Grab whatevers at the TOP of the stack!!!!!!!!!!
            self.StackPointer = self.StackPointer - 1 # DE crement to Remove the item 😈😈😈
        return Item #Woah

    # Look at the top item in the stack without removing it      
    def Peek(self):
        if self.StackPointer == -1: # IF its empty THEN give UP!!!!!!!!!!
            return None #LOL!!!!!!!!!!!!
        return self.Contents[self.StackPointer] # The Item 🤩🤩🤩🤩
    

#############################################################################
# Main program starts here

# Subroutine to output the contents of a stack

def ClearStack(InputStack):
    Item = InputStack.Peek()
    while Item:
        Item = InputStack.Pop()
        if Item:
            print(Item)

# How to create a new stack
MyStack = Stack()

#How to push to the stack (returns True on success or False on stack overflow)
Action = MyStack.Push("Craig")
Action = MyStack.Push("Dave")
Action = MyStack.Push("Crag")
Action = MyStack.Push("Burt")




# How to pop from the stack (stack underflow returns None)
#Item = MyStack.Pop(1)

print(MyStack.Peek())

print(MyStack.Contents)


