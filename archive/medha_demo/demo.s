	.file	"demo.c"
# GNU C23 (Ubuntu 15.2.0-16ubuntu1) version 15.2.0 (x86_64-linux-gnu)
#	compiled by GNU C version 15.2.0, GMP version 6.3.0, MPFR version 4.2.2, MPC version 1.3.1, isl version isl-0.27-GMP

# GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072
# options passed: -mtune=generic -march=x86-64 -O0 -fasynchronous-unwind-tables -fstack-protector-strong -fstack-clash-protection -fcf-protection -fzero-init-padding-bits=all
	.text
	.globl	create_node
	.type	create_node, @function
create_node:
.LFB6:
	.cfi_startproc
	endbr64	
	pushq	%rbp	#
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp	#,
	.cfi_def_cfa_register 6
	subq	$32, %rsp	#,
	movl	%edi, -20(%rbp)	# data, data
# /home/kanak/Desktop/ide/medha_demo/demo.c:12:     Node* n = (Node*)malloc(sizeof(Node));
	movl	$24, %edi	#,
	call	malloc@PLT	#
	movq	%rax, -8(%rbp)	# tmp100, n
# /home/kanak/Desktop/ide/medha_demo/demo.c:13:     n->data = data;
	movq	-8(%rbp), %rax	# n, tmp101
	movl	-20(%rbp), %edx	# data, tmp102
	movl	%edx, (%rax)	# tmp102, n_3->data
# /home/kanak/Desktop/ide/medha_demo/demo.c:14:     n->next = NULL;
	movq	-8(%rbp), %rax	# n, tmp103
	movq	$0, 8(%rax)	#, n_3->next
# /home/kanak/Desktop/ide/medha_demo/demo.c:15:     n->prev = NULL;
	movq	-8(%rbp), %rax	# n, tmp104
	movq	$0, 16(%rax)	#, n_3->prev
# /home/kanak/Desktop/ide/medha_demo/demo.c:16:     return n;
	movq	-8(%rbp), %rax	# n, _8
# /home/kanak/Desktop/ide/medha_demo/demo.c:17: }
	leave	
	.cfi_def_cfa 7, 8
	ret	
	.cfi_endproc
.LFE6:
	.size	create_node, .-create_node
	.section	.rodata
	.align 8
.LC0:
	.string	"MEDH\304\200 IDE C Demo: Doubly Linked List [10 <-> 20 <-> 30]"
	.text
	.globl	main
	.type	main, @function
main:
.LFB7:
	.cfi_startproc
	endbr64	
	pushq	%rbp	#
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp	#,
	.cfi_def_cfa_register 6
	pushq	%rbx	#
	subq	$24, %rsp	#,
	.cfi_offset 3, -24
# /home/kanak/Desktop/ide/medha_demo/demo.c:20:     Node* head = create_node(10);
	movl	$10, %edi	#,
	call	create_node	#
	movq	%rax, -24(%rbp)	# tmp107, head
# /home/kanak/Desktop/ide/medha_demo/demo.c:21:     head->next = create_node(20);
	movl	$20, %edi	#,
	call	create_node	#
# /home/kanak/Desktop/ide/medha_demo/demo.c:21:     head->next = create_node(20);
	movq	-24(%rbp), %rdx	# head, tmp108
	movq	%rax, 8(%rdx)	# _1, head_10->next
# /home/kanak/Desktop/ide/medha_demo/demo.c:22:     head->next->prev = head;
	movq	-24(%rbp), %rax	# head, tmp109
	movq	8(%rax), %rax	# head_10->next, _2
# /home/kanak/Desktop/ide/medha_demo/demo.c:22:     head->next->prev = head;
	movq	-24(%rbp), %rdx	# head, tmp110
	movq	%rdx, 16(%rax)	# tmp110, _2->prev
# /home/kanak/Desktop/ide/medha_demo/demo.c:23:     head->next->next = create_node(30);
	movq	-24(%rbp), %rax	# head, tmp111
	movq	8(%rax), %rbx	# head_10->next, _3
# /home/kanak/Desktop/ide/medha_demo/demo.c:23:     head->next->next = create_node(30);
	movl	$30, %edi	#,
	call	create_node	#
# /home/kanak/Desktop/ide/medha_demo/demo.c:23:     head->next->next = create_node(30);
	movq	%rax, 8(%rbx)	# _4, _3->next
# /home/kanak/Desktop/ide/medha_demo/demo.c:24:     head->next->next->prev = head->next;
	movq	-24(%rbp), %rax	# head, tmp112
	movq	8(%rax), %rax	# head_10->next, _5
# /home/kanak/Desktop/ide/medha_demo/demo.c:24:     head->next->next->prev = head->next;
	movq	8(%rax), %rax	# _5->next, _6
# /home/kanak/Desktop/ide/medha_demo/demo.c:24:     head->next->next->prev = head->next;
	movq	-24(%rbp), %rdx	# head, tmp113
	movq	8(%rdx), %rdx	# head_10->next, _7
# /home/kanak/Desktop/ide/medha_demo/demo.c:24:     head->next->next->prev = head->next;
	movq	%rdx, 16(%rax)	# _7, _6->prev
# /home/kanak/Desktop/ide/medha_demo/demo.c:26:     printf("MEDHĀ IDE C Demo: Doubly Linked List [10 <-> 20 <-> 30]\n");
	leaq	.LC0(%rip), %rax	#, tmp114
	movq	%rax, %rdi	# tmp114,
	call	puts@PLT	#
# /home/kanak/Desktop/ide/medha_demo/demo.c:27:     return 0;
	movl	$0, %eax	#, _18
# /home/kanak/Desktop/ide/medha_demo/demo.c:28: }
	movq	-8(%rbp), %rbx	#,
	leave	
	.cfi_def_cfa 7, 8
	ret	
	.cfi_endproc
.LFE7:
	.size	main, .-main
	.ident	"GCC: (Ubuntu 15.2.0-16ubuntu1) 15.2.0"
	.section	.note.GNU-stack,"",@progbits
	.section	.note.gnu.property,"a"
	.align 8
	.long	1f - 0f
	.long	4f - 1f
	.long	5
0:
	.string	"GNU"
1:
	.align 8
	.long	0xc0000002
	.long	3f - 2f
2:
	.long	0x3
3:
	.align 8
4:
