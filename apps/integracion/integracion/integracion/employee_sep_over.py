from integracion.integracion.empl_onb_con_over import CustomEmployeeBoardingController


class CustomEmployeeSeparation(CustomEmployeeBoardingController):
	def validate(self):
		super().validate()

	def on_submit(self):
		super().on_submit()

	def on_update_after_submit(self):
		self.create_task_and_notify_user()

	def on_cancel(self):
		super().on_cancel()
