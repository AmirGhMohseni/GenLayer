# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

class FeedbackSystem(gl.Contract):
    # Store rating (u256) and comment (str) for each address
    ratings: TreeMap[Address, u256]
    comments: TreeMap[Address, str]
    # Use DynArray instead of list for persistent storage
    user_list: DynArray[Address]

    def __init__(self):
        self.ratings = TreeMap()
        self.comments = TreeMap()
        self.user_list = DynArray()

    # --- View methods (read-only) ---

    @gl.public.view
    def get_my_feedback(self) -> tuple[u256, str]:
        """
        Get the current user's rating and comment.
        Returns (0, "") if no feedback found.
        """
        sender = gl.message.sender_address
        rating = self.ratings.get(sender, 0)
        comment = self.comments.get(sender, "")
        return (rating, comment)

    @gl.public.view
    def get_feedback_by_address(self, account_address: str) -> tuple[u256, str]:
        """
        Get feedback for a specific address.
        """
        addr = Address(account_address)
        return (self.ratings.get(addr, 0), self.comments.get(addr, ""))

    @gl.public.view
    def get_all_users(self) -> DynArray[Address]:
        """
        Get a list of all addresses that have submitted feedback.
        """
        return self.user_list

    @gl.public.view
    def get_average_rating(self) -> u256:
        """
        Calculate and return the average rating of all users.
        Returns 0 if no ratings exist.
        """
        if len(self.user_list) == 0:
            return 0
        total = 0
        for addr in self.user_list:
            total += self.ratings.get(addr, 0)
        return total // len(self.user_list)

    # --- Write methods (state modification) ---

    @gl.public.write
    def submit_feedback(self, rating: u256, comment: str) -> None:
        """
        Submit or update rating and comment for the current user.
        Rating must be between 1 and 5 (inclusive). Invalid ratings are ignored.
        """
        if rating < 1 or rating > 5:
            return

        sender = gl.message.sender_address
        # If this user hasn't submitted before, add to user_list
        if self.ratings.get(sender, 0) == 0:
            self.user_list.append(sender)
        # Update the rating and comment
        self.ratings[sender] = rating
        self.comments[sender] = comment

    @gl.public.write
    def delete_feedback(self) -> None:
        """
        Remove the current user's feedback entirely.
        """
        sender = gl.message.sender_address
        if self.ratings.get(sender, 0) != 0:
            del self.ratings[sender]
            del self.comments[sender]
            # Remove from user_list (find and remove)
            # DynArray supports remove() method
            if sender in self.user_list:
                self.user_list.remove(sender)