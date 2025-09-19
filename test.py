class Solution:
    def removeDuplicates(self, nums):
        encountered = []
        i = 0
        while i < len(nums):
            if nums[i] not in encountered:
                encountered.append(nums[i])
            if nums[i] in encountered:
                nums.pop(i)
        return len(encountered),encountered
    
sol = Solution()
s = [1,2,2,2,3,4,5,6,6,6,7,8,9,9,9,10]
print(sol.removeDuplicates(s))